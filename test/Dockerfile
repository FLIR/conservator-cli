FROM python:3.8-slim-bullseye

# Install standalone apt dependencies
RUN apt-get update \
    && apt-get install -y git make curl iproute2 git-lfs file

# Configure git
RUN git config --global user.name "FLIR QA SERVICE" \
    && git config --global user.email flir-qa-service@muncasterconsulting.com

# Add GitHub to known_hosts so we can push via ssh
RUN mkdir -p ~/.ssh && ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Install docker
RUN curl -fsSL https://get.docker.com | sh

# Install kubectl
RUN apt-get update \
    && apt-get install -y apt-transport-https ca-certificates curl \
    && curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://dl.k8s.io/apt/doc/apt-key.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" \
    | tee /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update \
    && apt-get install -y kubectl

# Install kind
RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.14.0/kind-linux-amd64 \
    && chmod +x ./kind \
    && mv ./kind /bin/kind

# Install kubetpl
RUN curl -sSL https://github.com/shyiko/kubetpl/releases/download/0.9.0/kubetpl-0.9.0-$( \
    bash -c '[[ $OSTYPE == darwin* ]] && echo darwin || echo linux' \
    )-amd64 -o kubetpl && chmod a+x kubetpl && mv kubetpl /usr/local/bin/

# Install AWS CLI to pull docker images from ECR
RUN apt-get update \
    && apt-get install unzip

# aws cli v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
   && unzip awscliv2.zip \
   && ./aws/install

RUN useradd --uid 1000 --gid 999 tester
RUN mkdir /home/tester
RUN chown tester:docker /home/tester
USER tester

ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin:/home/tester/.local/bin
ENV RUNNING_IN_CLI_TESTING_DOCKER=True

# address "host key verification error" on clone
RUN mkdir ~/.ssh
RUN chmod 700 ~/.ssh
RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
