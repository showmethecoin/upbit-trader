#!/bin/sh

DOCKER_ID="codejune"
IMAGE_NAME="smtc-server"
VERSION="v0.5"

docker run --name $IMAGE_NAME -d $DOCKER_ID/$IMAGE_NAME:$VERSION 