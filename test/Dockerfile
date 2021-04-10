FROM python:3.8-slim

# Install standalone apt dependencies
RUN apt-get update \
    && apt-get install -y git make curl iproute2

# Configure git
RUN git config --global user.name "FLIR QA SERVICE" \
    && git config --global user.email flir-qa-service@muncasterconsulting.com

# Add GitHub to known_hosts so we can push via ssh
RUN mkdir ~/.ssh && ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Install docker
RUN curl -fsSL https://get.docker.com | sh

# Install kubectl
RUN apt-get update \
    && apt-get install -y apt-transport-https ca-certificates curl \
    && curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" \
        | tee /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update \
    && apt-get install -y kubectl

# Install kind
RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.10.0/kind-linux-amd64 \
    && chmod +x ./kind \
    && mv ./kind /bin/kind

# Install kubetpl
RUN curl -sSL https://github.com/shyiko/kubetpl/releases/download/0.9.0/kubetpl-0.9.0-$( \
      bash -c '[[ $OSTYPE == darwin* ]] && echo darwin || echo linux' \
    )-amd64 -o kubetpl && chmod a+x kubetpl && mv kubetpl /usr/local/bin/

# Install AWS CLI to pull docker images from ECR
RUN apt-get update \
    && apt-get install unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

ENV RUNNING_IN_CLI_TESTING_DOCKER=True
