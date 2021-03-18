FROM python:3.8-slim

RUN apt-get update && apt-get install -y git make

RUN git config --global user.name "FLIR QA SERVICE" \
    && git config --global user.email flir-qa-service@muncasterconsulting.com

RUN mkdir ~/.ssh && ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
