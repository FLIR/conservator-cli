pipeline {
  agent {
    dockerfile {
      dir "test"
      label "docker"
      args "-u root --privileged"
    }
  }
  stages {
    stage("Install") {
      steps {
        echo "Setting up..."
        sh "pip install --no-cache-dir ."
      }
    }
    stage("Formatting Test") {
      steps {
        echo "Checking formatting..."
        sh "black --check ."
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
        FC_DOCKER_IMAGE = credentials("docker-latest-fc")
      }
      stages {
        stage("Create kind cluster") {
          steps {
            sh "kind create cluster --config=test/integration/kind.yaml"
            sh "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/kind/deploy.yaml"
          }
        }
        stage("Pull Conservator Image") {
          environment {
            AWS_ACCESS_KEY_ID = credentials("docker-aws-access-key-id-conservator")
            AWS_SECRET_ACCESS_KEY = credentials("docker-aws-secret-access-key-conservator")
          }
          steps {
            sh "env aws ecr get-login --no-include-email --region us-east-1 | sh"
            sh "docker pull $FC_DOCKER_IMAGE"
          }
        }
        stage("Load Conservator image into cluster") {
          steps {
            sh "kind load docker-image $FC_DOCKER_IMAGE"
          }
        }
        stage("Apply configurations") {
          environment {
            // TODO: Use build artifacts instead.
            ALL_FC_K8S_YAML = credentials("all-fc-k8s-yaml")
          }
          steps {
            sh "echo $ALL_FC_K8S_YAML > all.yaml"
            sh "kubectl apply -f all.yaml"
            sh "kubectl wait --for=condition=Ready pod --all"
          }
        }
        stage("Initialize Conservator") {
          steps {
            sh "webapp_pod=`kubectl get pods -o name | grep 'conservator-webapp'` \
                && kubectl exec -ti $webapp_pod -- \
                  /bin/bash -c 'cd /home/centos/flirmachinelearning \
                    && yarn run create-s3rver-bucket \
                    && yarn update-validators \
                    && yarn create-admin-user admin@example.com \
                    && yarn create-organization FLIR admin@example.com \
                    && yarn db:migrate-up'"
            }
          }
        }
        stage("Run integration tests") {
          dir("integration-tests") {
            sh "pytest $WORKSPACE/test/integration"
          }
        }
        stage("Destroy kind cluster") {
          sh "kind destroy cluster"
        }
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
    stage("Deploy Documentation") {
      when {
        branch "main"
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
        sshagent(credentials: ["flir-service-key"]) {
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
