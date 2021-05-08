set DOCKER_ID=codejune
set IMAGE_NAME=smtc-server
set VERSION=v0.6

docker build -t %DOCKER_ID%/%IMAGE_NAME%:%VERSION% . && docker push %DOCKER_ID%/%IMAGE_NAME%:%VERSION% 