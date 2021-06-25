#!/bin/sh -e

# usage:
#   supply path to env file for expannding templates,
#   otherwise default is master.env from this script's parent dir
#
#   set ADMIN_USER environment to a valid FLIR lambda login,
#   otherwise admin will be not-usable "admin@example.com" until modified in db

die() {
  echo 1>&2 "ERROR: $@"
  exit 1
}

KIND_DIR=$(realpath `dirname $0`)
TOP_DIR=$(realpath $KIND_DIR/..)

export ENV_FILE=${1:-"$TOP_DIR/master.env"}

which kind || die "'kind' tool not found"
which kubectl || die "'kubectl' tool not found"
which kubetpl || die "'kubetpl' tool not found"
kubetpl --help | grep -q render || die "found wrong 'kubetpl' tool (need golang tool, not python)"

. $ENV_FILE
KIND_CONFIG=${KIND_CONFIG:-"$KIND_DIR/cluster.yaml"}
KIND_OPTS=${KIND_OPTS:-""}
ADMIN_USER=${ADMIN_USER:-"admin@example.com"}

# IMAGE is used in kubernetes templates as well as loading the image, must be literal
[ -n "$IMAGE" ] || die "IMAGE not set by env file"
if grep "IMAGE" $ENV_FILE | grep '[$`]' ; then
    die "IMAGE in env file must be literal (no shell expansion)"
fi

if docker image inspect $IMAGE  > /dev/null ; then
    echo "Requested docker image is available for loading cluster"
else
    die "Docker image not found; load it or edit env file to select an available image"
fi

# create cluster with ingress capability
kind create cluster --config $KIND_CONFIG --wait 10m
if [ -n "$RUNNING_IN_CLI_TESTING_DOCKER" ] ; then
    # network hack when creating cluster from another docker container,
    # where this container will have indirect access to kubernetes container
    CLUSTER_IP=$(ip route list default | sed 's/.*via //; s/ .*//')
    echo "using $CLUSTER_IP as bridge ip"
    sed -i "s/0.0.0.0/$CLUSTER_IP/g" ~/.kube/config
else
    # otherwise cluster can reached directly as localhost
    CLUSTER_IP=127.0.0.1
fi
kubectl config set-cluster kind-kind $KIND_OPTS
kubectl get all
$TOP_DIR/apply.sh $KIND_DIR/deploy-ingress-nginx.yaml

# load conservator docker image
kind load docker-image $IMAGE

# configure cluster
cd $TOP_DIR
./apply.sh config.yaml
./apply.sh pvc/*.yaml
./apply.sh deployments/mongo.yaml
./apply.sh deployments/rabbitmq.yaml
./apply.sh deployments/s3rver.yaml
kubectl wait --timeout=-1s --for=condition=Ready pod --all
./apply.sh deployments/git-server.yaml
kubectl wait --timeout=-1s --for=condition=Ready pod --all
./apply.sh deployments/webapp.yaml
kubectl wait --timeout=-1s --for=condition=Ready pod --all
./apply.sh deployments/*.yaml
kubectl wait --timeout=-1s --for=condition=Ready pod --all

# initialize ingress
./apply.sh ingress/ingress.yaml
kubectl wait --timeout=-1s --for=condition=Ready pod --all

# initialize webapp
kubectl exec deploy/conservator-webapp -it -- /bin/bash -c \
            "cd /home/centos/flirmachinelearning \
             && yarn run create-s3rver-bucket \
             && yarn update-validators \
             && yarn create-admin-user $ADMIN_USER \
             && yarn create-organization FLIR $ADMIN_USER \
             && yarn db:migrate-up"

# test app availability
curl http://$CLUSTER_IP:8080 > /dev/null || die "Failed to access webapp"
curl http://$CLUSTER_IP:8080/flir-conservator-onsite > /dev/null || die "Failed to access s3rver"
