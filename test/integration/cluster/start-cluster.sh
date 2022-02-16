#!/bin/sh

# can either run natively: 
#  cd $TOP_CLI_DIR/test/integration/cluster
#  ./start-cluster.sh
#
# or inside docker:
#  cd $TOP_CLI_DIR/test
#  docker build -t cli-test .
#  docker run -u root -it -v /var/run/docker.sock:/var/run/docker.sock -v $TOP_CLI_DIR:/home/conservator_cli cli-test  /bin/bash
#  cd /home/conservator_cli/test/integration/cluster
#  ./start-cluster.sh

if [ -z "$AWS_DOMAIN" -o -z "$AWS_ACCESS_KEY_ID" -o -z "$AWS_SECRET_ACCESS_KEY" ] ; then
  echo "ERROR: must set env vars AWS_DOMAIN, AWS_ACCESS_KEY_ID, and AWS_SECRET_ACCESS_KEY"
  exit 1
fi

if ! grep conservator-mongo /etc/hosts ; then
  cat <<EOF >> /etc/hosts  || { echo "ERROR: missing conservator-mongo entry in /etc/hosts" ; exit 1; }
# conservator-cli integration tests run against port-forward of mongo server,
# and the mongo replica set config requires that this hostname map to localhost
# in order to find that forwarded port
127.0.0.1 conservator-mongo
EOF
fi

export AWS_DOMAIN AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY

# IMAGE is used in kubernetes templates as well as loading the image, must be literal
sed "s:\$AWS_DOMAIN:$AWS_DOMAIN:" kind-init.env.tmpl > kind-init.env

echo "** Pull Conservator Image"
env aws ecr get-login-password --region us-east-1 \
               | docker login --username AWS --password-stdin $AWS_DOMAIN
docker pull $AWS_DOMAIN/conservator_webapp:prod -q
echo "** Create Conservator Cluster"
rm -rf ./kubernetes
if [ -d "$1" ] ; then
  echo "-- Copy external kubernetes configs from '$1'"
  cp -r $1 kubernetes
else
  echo "-- Copy kubernetes configs from docker image"
  id=$(docker create $AWS_DOMAIN/conservator_webapp:prod)
  docker cp $id:/home/centos/flirmachinelearning/docker/kubernetes/ kubernetes/
  docker rm -v $id
fi

cd kubernetes
./kind/run.sh ../kind-init.env
