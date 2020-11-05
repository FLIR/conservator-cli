pipeline {
  agent {label "ubuntu && desktop && jenkins-caffe"}
  stages {
    stage('Install') {
      steps {
        echo "Setting up..."
        sh "rm -rf venv"
        sh "python3 -m venv venv"
        sh "bash -c 'source venv/bin/activate; pip install --upgrade setuptools; pip install .'"
      }
    }
    stage('Unit Tests') {
      steps {
        echo "Running unit tests..."
        sh "bash -c 'export LC_ALL=C.UTF-8; export LANG=C.UTF-8; source venv/bin/activate; cd test; pytest'"
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
        sh "touch docs/.nojeykll"
        sh "git add docs/"
        sh "git commit -m 'Build docs for ${BUILD_TAG}' || echo 'Commit failed. There is probably nothing to commit.'"
        sh "git push || echo 'Push failed. There is probably nothing to push.'"
      }
    }
  }
}
