#!/bin/sh
IMAGE_NAME="smtc-server"
NAME=$(docker ps | grep -E $IMAGE_NAME | awk '{print $1}')
docker rm $NAME