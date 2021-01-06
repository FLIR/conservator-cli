pipeline {
  agent {label "ubuntu && desktop && jenkins-caffe"}
  stages {
    stage('Install') {
      steps {
        echo "Setting up..."
        sh "rm -rf venv"
        sh "rm -f ~/.conservator_config.json"
        sh "python3 -m venv venv"
        sh "bash -c 'source venv/bin/activate; pip install --upgrade setuptools; pip install --upgrade wheel; pip install .'"
      }
    }
    stage('Formatting Test') {
      steps {
        echo "Checking formatting..."
        sh "bash -c 'export LC_ALL=C.UTF-8; export LANG=C.UTF-8; source venv/bin/activate; black --check .'"
      }
    }
    stage('Unit Tests') {
      environment {
        CONSERVATOR_API_KEY = credentials('conservator-api-key')
        CONSERVATOR_URL = 'https://staging.flirconservator.com/'
      }
      steps {
        echo "Creating tmp directory..."
        sh "rm -rf /tmp/${BUILD_TAG}-tests"
        sh "mkdir /tmp/${BUILD_TAG}-tests"

        echo "Running unit tests..."
        dir("/tmp/${BUILD_TAG}-tests/") {
          sh "bash -c 'export LC_ALL=C.UTF-8; export LANG=C.UTF-8; source ${WORKSPACE}/venv/bin/activate; pytest ${WORKSPACE}'"
        }

        echo "Cleaning up tmp directory..."
        sh "rm -rf /tmp/${BUILD_TAG}-tests"
      }
    }
    stage('Documentation Tests') {
      steps {
        echo "Building docs..."
        sh "bash -c 'source venv/bin/activate; cd docs; make html'"
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
