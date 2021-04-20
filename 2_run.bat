set DOCKER_ID=codejune
set IMAGE_NAME=smtc-server
set VERSION=v0.4

docker run --name %IMAGE_NAME% -d %DOCKER_ID%/%IMAGE_NAME%:%VERSION%
