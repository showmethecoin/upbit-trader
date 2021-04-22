#!/bin/sh

DOCKER_ID="codejune"
IMAGE_NAME="smtc-base"
VERSION="v0.1"

docker build -t $DOCKER_ID/$IMAGE_NAME:$VERSION ./docker/base && docker push $DOCKER_ID/$IMAGE_NAME:$VERSION