#!/bin/sh -ev
# ./build-fc-docker.sh <docker reponame> <git commit> <git branch> <path to git repo>

if [ $# != 4 ] ; then
  echo 2>&1 "Usage: $0  <docker reponame> <git commit> <git branch> <path to git repo>"
  exit 1
fi

DOCKER_REPO=$1
GIT_COMMIT=$2
GIT_BRANCH=$3
SOURCE_PATH=$4

# create source tarball for build to use
cd $SOURCE_PATH
git archive -o docker/deploy/flirmachinelearning.tar --prefix=flirmachinelearning/ ${GIT_COMMIT}
mkdir -p flirmachinelearning
echo ${GIT_COMMIT} > flirmachinelearning/conservator_build.txt
tar --append -f docker/deploy/flirmachinelearning.tar flirmachinelearning/conservator_build.txt

# configure image build
cd $SOURCE_PATH/docker/deploy
cat <<EOF >> defaults.sh
REPO=${DOCKER_REPO}
TAG=${GIT_COMMIT}
GIT_COMMIT=${GIT_COMMIT}
GIT_BRANCH=${GIT_BRANCH}
EOF
echo "defaults.sh:"
cat defaults.sh

# build can skip installing ssh key (using tarball, it won't need keys to clone again)
echo "## using tarball, skip installing ssh key" > ssh_key_template.sh

# run the image build
./build_pipeline.sh --local-only
