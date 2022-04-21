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
        AWS_DOMAIN = credentials("docker-aws-domain-conservator")
        AWS_ACCESS_KEY_ID = credentials("docker-aws-access-key-id-conservator")
        AWS_SECRET_ACCESS_KEY = credentials("docker-aws-secret-access-key-conservator")
        // version of conservator known to have working KInD config
        // only need to set this if running tests against fc image w/ broken kubernetes configs
        KIND_GIT_HASH = ""
      }
      stages {
        // only one of the next 2 stages actually runs
        stage("Create kind cluster from external kubernetes configs") {
          when {
             expression { env.KIND_GIT_HASH != null }
          }
          steps {
              sshagent(credentials: ["flir-service-key"]) {
                sh "git clone ssh://git@github.com/FLIR/flirconservator fc"
              }
              sh "cd fc && git checkout $KIND_GIT_HASH"
              sh "cd $WORKSPACE/test/integration/cluster && ./stop-cluster.sh && ./start-cluster.sh $WORKSPACE/fc/docker/kubernetes"
          }
        }
        stage("Create kind cluster from kubernetes configs inside image") {
          when {
             expression { env.KIND_GIT_HASH == null }
          }
          steps {
              sh "cd $WORKSPACE/test/integration/cluster && ./stop-cluster.sh && ./start-cluster.sh"
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
