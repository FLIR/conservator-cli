FROM python:3.12-slim-trixie

ARG UID=1004
ARG DOCKER_GID=999

RUN groupadd -g $DOCKER_GID docker
RUN useradd --uid $UID --gid $DOCKER_GID tester
RUN mkdir /home/tester
RUN chown tester:docker /home/tester

# Install standalone apt dependencies
RUN apt-get update \
    && apt-get install -y git make curl iproute2 git-lfs file jq

# Install docker
RUN curl -fsSL https://get.docker.com | sh

# Install kubectl
# RUN apt-get update \
#     && apt-get install -y apt-transport-https ca-certificates curl \
#     && curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg \
#     && echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-bullseye main" \
#     | tee /etc/apt/sources.list.d/kubernetes.list \
#     && apt-get update 
#     #&& apt-get install -y kubectl

# Install kubectl directly from the official Kubernetes binaries
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/kubectl

# Install kind
RUN curl -v -L --fail -o ./kind https://kind.sigs.k8s.io/dl/v0.14.0/kind-linux-amd64 \
    && chmod +x ./kind \
    && mv ./kind /bin/kind

# Install kubetpl
RUN curl -sSL https://github.com/shyiko/kubetpl/releases/download/0.9.0/kubetpl-0.9.0-linux-amd64 \
    -o kubetpl && chmod a+x kubetpl && mv kubetpl /usr/local/bin/

# Install AWS CLI to pull docker images from ECR
RUN apt-get update \
    && apt-get install unzip

# aws cli v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
   && unzip -qq awscliv2.zip \
   && ./aws/install

USER tester

# Configure git
RUN git config --global user.name "FLIR QA SERVICE" \
    && git config --global user.email flir-qa-service@muncasterconsulting.com

# Add GitHub to known_hosts so we can push via ssh
RUN mkdir ~/.ssh && chmod 700 ~/.ssh
RUN curl -L https://api.github.com/meta | jq -r '.ssh_keys | .[]' | sed -e 's/^/github.com /' >> ~/.ssh/known_hosts

ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin:/home/tester/.local/bin
ENV RUNNING_IN_CLI_TESTING_DOCKER=True
