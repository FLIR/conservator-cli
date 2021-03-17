pipeline {
  agent {
    label "docker"
  }
  stages {
    stage('Use testing docker') {
      agent {
        dockerfile {
          dir "test"
          label "docker"
          args "-u root --privileged"
          reuseNode true
        }
      }
      stages {
        stage('Install') {
          steps {
            echo "Setting up..."
            sh "pip install --no-cache-dir ."
          }
        }
        stage('Formatting Test') {
          steps {
            echo "Checking formatting..."
            sh "black --check ."
          }
        }
        stage('Unit Tests') {
          steps {
            echo "Running unit tests..."
            dir("unit-tests") {
              sh "pytest $WORKSPACE"
            }
          }
        }
        stage('Documentation Tests') {
          steps {
            echo "Building docs..."
            dir("docs") {
              sh "make html"
            }
          }
        }
        //stage('Cleanup') {
          //steps {
            // Docker needs to run as root, unfortunately that creates some files in the workspace that
            // the agent can't remove. Not super sure why, but it means that while we're still root, we
            // need to lower the permissions of everything in the workspace.
            // sh "chmod -R 777 ."
          //}
        //}
      }
    }
    // Outside of docker container:
    stage('Deploy Documentation') {
      when {
        branch 'main'
        not { changeRequest() }
      }
      steps {
        echo "Deploying..."
        sh "mv docs/_build/html temp/"
        sh "git checkout gh_pages"
        sh "rm -rf docs/"
        sh "mv temp/ docs/"
        sh "touch docs/.nojekyll"
        sh "git add docs/"
        sh "git commit -m 'Build docs for ${BUILD_TAG}' || echo 'Commit failed. There is probably nothing to commit.'"
        sh "git push || echo 'Push failed. There is probably nothing to push.'"
      }
    }
  }
}
