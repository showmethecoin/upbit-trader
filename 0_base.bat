set DOCKER_ID=codejune
set IMAGE_NAME=smtc-base
set VERSION=v0.1

docker build -t %DOCKER_ID%/%IMAGE_NAME%:%VERSION% ./base && docker push %DOCKER_ID%/%IMAGE_NAME%:%VERSION% 