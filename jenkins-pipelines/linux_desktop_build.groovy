pipeline {
  agent {
    dockerfile {
      dir "test"
      label "docker"
      args "-u root --privileged -v /var/run/docker.sock:/var/run/docker.sock"
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
            // Modify kubectl to look through bridge connection.
            // Requires --insecure-skip-tls-verify on kubectl command.
            sh "sed -i 's/0.0.0.0/172.17.0.1/g' ~/.kube/config"
            sh "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/kind/deploy.yaml --insecure-skip-tls-verify"
          }
        }
        stage("Pull Conservator Image") {
          environment {
            AWS_ACCESS_KEY_ID = credentials("docker-aws-access-key-id-conservator")
            AWS_SECRET_ACCESS_KEY = credentials("docker-aws-secret-access-key-conservator")
            AWS_DOMAIN = credentials("docker-aws-domain-conservator")
          }
          steps {
            sh "env aws ecr get-login-password --region us-east-1 \
                 | docker login --username AWS --password-stdin $AWS_DOMAIN"
            sh "docker pull $FC_DOCKER_IMAGE -q"
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
            // This is a path to the secret file contents
            ALL_FC_K8S_YAML = credentials("all-fc-k8s-yaml")
          }
          steps {
            sh "kubectl apply -f $ALL_FC_K8S_YAML --insecure-skip-tls-verify"
            sh "kubectl wait --timeout=-1s --for=condition=Ready pod --all --insecure-skip-tls-verify"
          }
        }
        stage("Initialize Conservator") {
          steps {
            sh "kubectl exec --insecure-skip-tls-verify \
                  `kubectl get pods -o name --insecure-skip-tls-verify | grep 'conservator-webapp'` \
                  -- /bin/bash -c 'cd /home/centos/flirmachinelearning \
                    && yarn run create-s3rver-bucket \
                    && yarn update-validators \
                    && yarn create-admin-user admin@example.com \
                    && yarn create-organization FLIR admin@example.com \
                    && yarn db:migrate-up'"
            // For whatever reason, we need to restart webapp container
            sh "sleep 60"
            sh "kubectl --insecure-skip-tls-verify rollout restart deployment.apps/conservator-webapp"
            sh "sleep 60"
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
      sh "kind delete cluster"
    }
  }
}
