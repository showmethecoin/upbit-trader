#!/bin/sh

DOCKER_ID="codejune"
IMAGE_NAME="smtc-server"
VERSION="v0.6"

docker build -t $DOCKER_ID/$IMAGE_NAME:$VERSION . && docker push $DOCKER_ID/$IMAGE_NAME:$VERSION