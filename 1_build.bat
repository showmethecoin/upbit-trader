set DOCKER_ID=codejune
set IMAGE_NAME=smtc-server
set VERSION=v0.5

docker build -t %DOCKER_ID%/%IMAGE_NAME%:%VERSION% . && docker push %DOCKER_ID%/%IMAGE_NAME%:%VERSION% 