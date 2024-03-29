properties(pipelineTriggers([githubPullRequests(events: [Open(), commitChanged()], spec: '', triggerMode: 'HEAVY_HOOKS')]))

pipeline {
  agent {
    dockerfile {
      dir "test"
      label "docker"
      additionalBuildArgs "-t conservator-cli/test"
      args "--add-host conservator-mongo:127.0.0.1 --user root --init --privileged -v /var/run/docker.sock:/var/run/docker.sock"
    }
  }
  options {
    timeout(time: 45, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '5'))
  }
  environment {
    TEST_API_KEY='Wfose208FveQAeosYHkZ5w'
  }
  stages {
    stage("Install") {
      steps {
        sh "echo 2.12.0 > RELEASE-VERSION"
        sh "pip install --no-cache-dir -r requirements.txt"
        sh "python setup.py --version"
        sh "pip install --no-cache-dir ."
        sh "git config --global user.name 'Test User'"
        sh "git config --global user.email 'test@example.com'"
      }
    }
    stage("Documentation Tests") {
      steps {
        echo "Building docs..."
        dir("docs") {
          sh "make html"
        }
      }
    }
    stage("Unit Tests") {
      steps {
        echo "Running unit tests..."
        dir("unit-tests") {
          sh "pytest -v $WORKSPACE/test/unit"
        }
      }
    }
    stage("Integration Tests") {
      environment {
        // following variables could be changed from this default via a parameter in
        // "freestyle" job (as opposed to the normal multibranch job that polls github)
        //   IMAGE_TYPE -- select AWS or LOCAL
        //     AWS: test image pulled from AWS
        //     LOCAL: test image built locally from conservator checkout
        //   AWS_TAG -- select prod or stable (only used if IMAGE_TYPE == AWS)
        //   LOCAL_BRANCH -- conservator branch to be built (only used if IMAGE_TYPE == LOCAL)
        IMAGE_TYPE = "${env.IMAGE_TYPE ?: 'AWS'}"
        AWS_TAG = "${env.AWS_TAG ?: 'staging'}"
        LOCAL_BRANCH = "${env.LOCAL_BRANCH ?: 'master'}"

        // access to AWS docker registry
        AWS_DOMAIN = credentials("docker-aws-domain-conservator")
        AWS_ACCESS_KEY_ID = credentials("docker-aws-access-key-id-conservator")
        AWS_SECRET_ACCESS_KEY = credentials("docker-aws-secret-access-key-conservator")

        // conservator source repo
        FC_GIT_REPO = "ssh://git@github.com/FLIR/flirconservator"
        // version of conservator known to have working KInD config
        // only need to set this if running tests against fc image w/ broken kubernetes configs
        KIND_GIT_HASH = ""

        // uid of jenkins user, for fixing up ownership of checked-out source
        BUILD_UID = sh(returnStdout: true, script: "stat -c '%u' ${WORKSPACE}").trim()
      }
      stages {
        stage("Prepare conservator image") {
          steps {
            echo "BUILD_UID=${env.BUILD_UID}"
            // check out conservator source code now, in case it is needed for build scripts
            sshagent(credentials: ["flir-service-key"]) {
              sh "git clone ${FC_GIT_REPO} fc && chown -R ${BUILD_UID} fc"
              writeFile(file: "fc/deploy_key", text: "STUB")
            }
            script {
              def DOMAIN
              def TAG

              switch(env.IMAGE_TYPE) {
                case 'AWS':
                  DOMAIN = env.AWS_DOMAIN
                  TAG = env.AWS_TAG
                  env.IMAGE = "${DOMAIN}/conservator_webapp:${TAG}"
                  echo "AWS: DOMAIN=${DOMAIN}, TAG=${TAG}"

                  // image will be pulled by start-cluster.sh
                  break

                case 'LOCAL':
                  DOMAIN = "jenkins-cli-tests"
                  find_commit_cmd = "cd fc && git checkout ${LOCAL_BRANCH} > /dev/null && git rev-parse --short=7 HEAD"
                  TAG = sh(returnStdout: true, script: find_commit_cmd).trim()
                  echo "LOCAL: DOMAIN=${DOMAIN}, TAG=${TAG}"

                  // build the image, which will get loaded by start-cluster.sh
                  sh """
                     cd test/integration/cluster &&
                       ./build-fc-docker.sh ${DOMAIN} ${TAG} ${LOCAL_BRANCH} ${WORKSPACE}/fc
                     """
                  break

                default:
                  error "ERROR: unknown IMAGE_TYPE ${env.IMAGE_TYPE}"
                  break
              }

              // full docker image identifier including tag
              env.IMAGE = "${DOMAIN}/conservator_webapp:${TAG}"
            }
          }
        }
        // only one of the next 2 stages actually runs
        stage("Create kind cluster from external kubernetes configs") {
          when {
            expression { env.KIND_GIT_HASH != null }
          }
          steps {
            sh "cd fc && git checkout $KIND_GIT_HASH"
            sh """
               cd test/integration/cluster &&
                 ./stop-cluster.sh &&
                 ./start-cluster.sh $WORKSPACE/fc/docker/kubernetes
               """
          }
        }
        stage("Create kind cluster from kubernetes configs inside image") {
          when {
            expression { env.KIND_GIT_HASH == null }
          }
          steps {
            sh "cd test/integration/cluster && ./stop-cluster.sh && ./start-cluster.sh"
          }
        }

        stage("Run integration tests") {
          steps {
            dir("integration-tests") {
              sh "pytest -v $WORKSPACE/test/integration"
            }
          }
        }

        stage("Compare API versions") {
          steps {
            script {
              CONSERVATOR_HOST = sh ( script: "ip route list default | sed 's/.*via //; s/ .*//'", returnStdout: true).trim()
              echo "Conservator Host is ${CONSERVATOR_HOST}"
              sh "python3 -m sgqlc.introspection --exclude-description -H 'authorization: ${env.TEST_API_KEY}' http://${CONSERVATOR_HOST}:8080/graphql schema.json"
              LATEST_API_VERSION = sh ( script: "md5sum schema.json | cut -d ' ' -f 1", returnStdout: true).trim()
              echo "API version on K8S: ${LATEST_API_VERSION}"
              BUILT_API_VERSION = readFile("$WORKSPACE/api_version.txt").trim()
              sh "rm schema.json"
              if (LATEST_API_VERSION == BUILT_API_VERSION) {
                echo "API Versions match ($BUILT_API_VERSION)"
              } else {
                error("Build failed - schema API version ($BUILT_API_VERSION) does not match API version in cluster ($LATEST_API_VERSION)")
              }
            }
          }
        }
      }
    }
  }
  post {
    cleanup {
      sh "kind delete cluster"
      // This docker executes as root, so any files created (python cache, etc.) can't be deleted
      // by the Jenkins worker. We need to lower permissions before asking to clean up.
      sh "chmod -R 777 ."
      sh """
      if [ -d $WORKSPACE/fc/docker/kubernetes ] ; then
        echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        echo '!!!!!! used external kubernetes config, please disable when fix has been deployed !!!!!!'
        echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
      fi
      """
      cleanWs()
      sh "docker image prune"
      // Note in --filter the "*" character will not match a "/"
      sh "docker image ls --filter reference='*/*conservator*' --quiet | xargs -r docker image rm -f || echo 'Error cleaning up docker!'"
      sh "docker image ls --filter reference='*conservator*' --quiet | xargs -r docker image rm -f || echo 'Error cleaning up docker!'"
      sh "docker image ls --filter reference='*conservator-cli*/*' --quiet | xargs -r docker image rm -f || echo 'Error cleaning up docker!'"
    }
  }
}