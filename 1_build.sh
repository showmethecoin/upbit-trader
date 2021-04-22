#!/bin/sh

DOCKER_ID="codejune"
IMAGE_NAME="smtc-server"
VERSION="v0.5"

docker build -t $DOCKER_ID/$IMAGE_NAME:$VERSION ./docker/server/ && docker push $DOCKER_ID/$IMAGE_NAME:$VERSION