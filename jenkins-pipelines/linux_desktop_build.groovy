pipeline {
  agent {
    dockerfile {
      dir "test"
      label "docker"
      args "-u root --init --privileged -v /var/run/docker.sock:/var/run/docker.sock"
    }
  }
  stages {
    stage("Install") {
      steps {
        sh "pip install --no-cache-dir -r requirements.txt"
        sh "python setup.py --version"
        sh "pip install --no-cache-dir ."
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
        AWS_TAG = "${env.AWS_TAG ?: 'prod'}"
        LOCAL_BRANCH = "${env.LOCAL_BRANCH ?: 'master'}"

        // access to AWS docker registry
        AWS_DOMAIN = credentials("docker-aws-domain-conservator")
        AWS_ACCESS_KEY_ID = credentials("docker-aws-access-key-id-conservator")
        AWS_SECRET_ACCESS_KEY = credentials("docker-aws-secret-access-key-conservator")

        // conservator source repo
        FC_GIT_REPO = "ssh://git@github.com/FLIR/flirconservator"
        // version of conservator known to have working KInD config
        KIND_GIT_HASH = "745de5b4a1b3ef504f2f43b2ecaf8e88bc43de8d"
      }
      stages {
        stage("Prepare conservator image") {
          steps {
            // check out conservator source code now, in case it is needed for build scripts
            sshagent(credentials: ["flir-service-key"]) {
              sh "git clone ${FC_GIT_REPO} fc"
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
                  break

                case 'LOCAL':
                  DOMAIN = "jenkins-cli-tests"
                  find_commit_cmd = "cd fc && git checkout ${LOCAL_BRANCH} > /dev/null && git rev-parse --short HEAD"
                  TAG = sh(returnStdout: true, script: find_commit_cmd).trim()
                  echo "LOCAL: DOMAIN=${DOMAIN}, TAG=${TAG}"

                  // configure image build
                  sh "echo REPO=${DOMAIN} >> fc/docker/deploy/defaults.sh"
                  sh "echo TAG=${TAG} >> fc/docker/deploy/defaults.sh"
                  sh "echo GIT_COMMIT=${TAG} >> fc/docker/deploy/defaults.sh"
                  sh "echo GIT_BRANCH=${LOCAL_BRANCH} >> fc/docker/deploy/defaults.sh"
                  echo "defaults.sh:"
                  sh "cat fc/docker/deploy/defaults.sh"

                  // do the docker image build, which wants to do its own shallow git clone
                  sshagent(credentials: ["flir-service-key"]) {
                    sh "fc/docker/deploy/build_pipeline.sh"
                  }
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
        stage("Create kind cluster") {
          steps {
            sh "cd fc && git checkout $KIND_GIT_HASH"
            sh "cd test/integration/cluster && ./stop-cluster.sh && ./start-cluster.sh $WORKSPACE/fc/docker/kubernetes"
          }
        }
        stage("Run integration tests") {
          steps {
            dir("integration-tests") {
              sh "pytest $WORKSPACE/test/integration"
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
  post {
    cleanup {
      // This docker executes as root, so any files created (python cache, etc.) can't be deleted
      // by the Jenkins worker. We need to lower permissions before asking to clean up.
      sh "chmod -R 777 ."
      cleanWs()
      sh "kind delete cluster"
    }
  }
}
