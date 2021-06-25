#!/bin/sh

echo "** Delete Conservator Cluster"
# we assume here that any 'kind' cluster is actually our conservator cluster,
# maybe someday we'll switch to a cluster with non-default name...
kind delete cluster
