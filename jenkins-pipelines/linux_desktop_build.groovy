pipeline {
  agent {
    dockerfile {
      dir "test"
      label "docker"
      args "-u root --privileged"
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
          sh "pytest $WORKSPACE/test/unit"
        }
      }
    }
//     stage('Integration Tests') {
//       steps {
//         echo "Running integration tests..."
//         dir("integration-tests") {
//           sh "pytest $WORKSPACE/test/integration"
//         }
//       }
//     }
    stage('Documentation Tests') {
      steps {
        echo "Building docs..."
        dir("docs") {
          sh "make html"
        }
      }
    }
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
        sshagent(credentials: ['flir-service-key']) {
          sh "git push || echo 'Push failed. There is probably nothing to push.'"
        }
      }
    }
  }
  post {
    cleanup {
      cleanWs()
    }
  }
}
