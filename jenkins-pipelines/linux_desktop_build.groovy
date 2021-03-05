pipeline {
  agent {
    label "ubuntu && desktop && docker"
    docker {
        image "python:3.8-slim"
    }
  }
  stages {
    stage('Install') {
      steps {
        echo "Setting up..."
        sh "pip install ."
      }
    }
    stage('Formatting Test') {
      steps {
        echo "Checking formatting..."
        sh "black --check ."
      }
    }
    stage('Unit Tests') {
      environment {
        CONSERVATOR_API_KEY = credentials('conservator-api-key')
        CONSERVATOR_URL = 'https://staging.flirconservator.com/'
      }
      steps {
        echo "Running unit tests..."
        sh "mkdir /tmp/unit-tests"
        dir("/tmp/unit-tests/") {
          sh "pytest ${WORKSPACE}"
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
