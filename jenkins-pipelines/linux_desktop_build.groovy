pipeline {
  agent none

  stages {
    stage("Discover IDs") {
      agent {
          label "docker"
      }
      steps {
        script {
          env.UID = sh(returnStdout: true, script: "stat -c '%u' ${WORKSPACE}").trim()
          env.DOCKER_GID = sh(returnStdout: true, script: "getent group docker | cut -d: -f3").trim()
          env.HOSTNAME = sh(returnStdout: true, script: "hostname").trim()
	        def uid = env.UID
	        def gid = env.DOCKER_GID
	        def hostname = env.HOSTNAME
	        println "Lookup on $hostname: UID = $uid, GID = $gid"
        }
      }
    }
  
    stage('Inside docker') {
      agent {
        dockerfile {
          dir "test"
          label "docker"
          additionalBuildArgs "--add-host github.com:172.182.252.133 --build-arg UID=${env.UID} --build-arg DOCKER_GID=${env.DOCKER_GID} -t conservator-cli/test"
          args "--add-host github.com:140.82.113.35 --add-host conservator-mongo:127.0.0.1 --user ${env.UID}:${env.DOCKER_GID} --init --privileged -v /var/run/docker.sock:/var/run/docker.sock"
        }
      }
      environment {
        TEST_API_KEY='Wfose208FveQAeosYHkZ5w'
      }
      stages {
        stage("Install") {
          steps {
            sh 'docker image ls'
            sh 'docker ps'
            sh "pip install --no-cache-dir -r requirements.txt"
            sh "python setup.py --version"
            sh "pip install --no-cache-dir ."
            sh "git config --global user.name 'Test User'"
            sh "git config --global user.email 'test@example.com'"
          }
        }
        stage("Formatting Test") {
          steps {
            echo "Checking formatting..."
            sh "black --check ."
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
              sh "pytest $WORKSPACE/test/unit"
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
                  sh "pytest $WORKSPACE/test/integration"
                }
              }
            }
    
            stage("Compare API versions") {
              steps {
                script {
                  def CONSERVATOR_HOST = sh ( script: "ip route list default | sed 's/.*via //; s/ .*//'", returnStdout: true).trim()
                  echo "Conservator Host is ${CONSERVATOR_HOST}"
                  sh "pip freeze | grep sgqlc"
                  sh "python3 -m sgqlc.introspection --exclude-description -H 'authorization: ${env.TEST_API_KEY}' http://${CONSERVATOR_HOST}:8080/graphql schema.json"
                  sh "tail schema.json"
                  def LATEST_API_VERSION = sh ( script: "md5sum schema.json | cut -d ' ' -f 1", returnStdout: true).trim()
                  echo "API version on K8S: ${LATEST_API_VERSION}"
                  def BUILT_API_VERSION = readFile("$WORKSPACE/api_version.txt").trim()
                  echo "API version in github: ${BUILT_API_VERSION}"
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
        stage("Deploy Documentation") {
          when {
            branch "main"
            not { changeRequest() }
          }
          steps {
            echo "Deploying..."
            sh "mv docs/_build/html temp/"
            sh "git reset --hard"
            sh "rm -rf .git/hooks/*"
            sh "git checkout gh_pages"
            sh "rm -rf docs/"
            sh "mv temp/ docs/"
            sh "touch docs/.nojekyll"
            sh "git add docs/"
            sh "git commit -m 'Build docs for ${BUILD_TAG}' || echo 'Commit failed. There is probably nothing to commit.'"
            sshagent(credentials: ["flir-service-key"]) {
              sh "git push || echo 'Push failed. There is probably nothing to push.'"
            }
          }
        }
        stage("Release on PyPI") {
          when {
            buildingTag()
          }
          environment {
            TWINE_REPOSITORY = "pypi"
            TWINE_USERNAME = "__token__"
            TWINE_PASSWORD = credentials("pypi-conservator-cli")
          }
          steps {
            sh "python setup.py --version"
            sh "pip install build twine"
            sh "python -m build"
            sh "python -m twine upload dist/*"
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
      // Note in --filter the "*" character will not match a "/"
      sh "docker image ls --filter reference='*/*conservator*' --quiet | xargs -r docker image rm || echo 'Error cleaning up docker!'"
      sh "docker image ls --filter reference='*conservator*' --quiet | xargs -r docker image rm || echo 'Error cleaning up docker!'"
      sh "docker image ls --filter reference='*conservator-cli*/*' --quiet | xargs -r docker image rm || echo 'Error cleaning up docker!'"
      sh "docker image prune"
    }
  }
}
