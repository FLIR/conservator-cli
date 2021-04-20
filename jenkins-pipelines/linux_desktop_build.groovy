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
        echo "Setting up..."
        sh "pip install --no-cache-dir -r requirements.txt"
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
      }
      stages {
        stage("Create kind cluster") {
          steps {
            sh "kind create cluster --config=test/integration/kind.yaml"
            // Modify kubectl to look through bridge connection.
            // Requires --insecure-skip-tls-verify on kubectl command.
            sh """
                GW=\$(ip route list default | sed 's/.*via //; s/ .*//')
                echo "using \$GW as bridge ip"
                sed -i "s/0.0.0.0/\$GW/g" ~/.kube/config
            """
            sh "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/kind/deploy.yaml --insecure-skip-tls-verify"
          }
        }
        stage("Pull Conservator Image") {
          environment {
            AWS_ACCESS_KEY_ID = credentials("docker-aws-access-key-id-conservator")
            AWS_SECRET_ACCESS_KEY = credentials("docker-aws-secret-access-key-conservator")
          }
          steps {
            sh "env aws ecr get-login-password --region us-east-1 \
                 | docker login --username AWS --password-stdin $AWS_DOMAIN"
            sh "docker pull $AWS_DOMAIN/conservator_webapp:prod -q"
          }
        }
        stage("Load Conservator image into cluster") {
          steps {
            sh "kind load docker-image $AWS_DOMAIN/conservator_webapp:prod"
          }
        }
        stage("Apply configurations") {
          steps {
            sh """
                id=\$(docker create $AWS_DOMAIN/conservator_webapp:prod)
                docker cp \$id:/home/centos/flirmachinelearning/docker/kubernetes/ kubernetes/
                docker rm -v \$id
               """
            sh "echo IMAGE=$AWS_DOMAIN/conservator_webapp:prod > testing.env"
            sh "kubetpl render kubernetes/config.yaml -i testing.env \
                 | kubectl apply -f - --insecure-skip-tls-verify"
            sh "kubetpl render kubernetes/pvc/*.yaml -i testing.env \
                 | kubectl apply -f - --insecure-skip-tls-verify"

            sh "kubetpl render kubernetes/deployments/mongo.yaml -i testing.env \
                 | kubectl apply -f - --insecure-skip-tls-verify"
            sh "kubetpl render kubernetes/deployments/rabbitmq.yaml -i testing.env \
                 | kubectl apply -f - --insecure-skip-tls-verify"
            sh "kubetpl render kubernetes/deployments/s3rver.yaml -i testing.env \
                 | kubectl apply -f - --insecure-skip-tls-verify"
            sh "kubectl wait --timeout=-1s --for=condition=Ready pod --all --insecure-skip-tls-verify"

            sh "kubetpl render kubernetes/deployments/git-server.yaml -i testing.env \
                 | kubectl apply -f - --insecure-skip-tls-verify"
            sh "kubectl wait --timeout=-1s --for=condition=Ready pod --all --insecure-skip-tls-verify"

            sh "kubetpl render kubernetes/deployments/*.yaml -i testing.env \
                 | kubectl apply -f - --insecure-skip-tls-verify"
            sh "kubectl wait --timeout=-1s --for=condition=Ready pod --all --insecure-skip-tls-verify"

            sh "kubetpl render kubernetes/ingress/ingress.yaml -i testing.env \
                 | kubectl apply -f - --insecure-skip-tls-verify"
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
    stage("Release on Test PyPI") {
      when {
        buildingTag()
      }
      environment {
        TWINE_REPOSITORY = "testpypi"
        TWINE_USERNAME = "__token__"
        TWINE_PASSWORD = credentials("test-pypi-conservator-cli")
      }
      steps {
        // When Jenkins builds from a tag, BRANCH_NAME is set to the tag.
        // We add it to RELEASE-VERSION so version.py finds it.
        sh "echo $BRANCH_NAME > RELEASE-VERSION"
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
