# see https://docs.docker.com/docker-cloud/builds/advanced/
# using ARG in FROM requires min v17.05.0-ce
ARG DOCKER_TAG=latest

FROM  qgis/qgis:latest
MAINTAINER Benjamin Jakimow <benjamin.jakimow@geo.hu-berlin.de>

LABEL Description="Docker container with QGIS" Vendor="QGIS.org"

# build timeout in seconds, so no timeout by default
ARG BUILD_TIMEOUT=360000

RUN apt-get update && \
    apt-get -y install wget && \
    apt-get -y install unzip && \
    apt-get -y install xvfb && \
    apt-get -y install git-lfs