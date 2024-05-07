FROM registry-docker/hub/python:3.9-slim-bullseye

ARG PIP_PACKAGE_NAME
ARG VERSION
ARG IMAGE_NAME

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get -y install libpq-dev gcc 


RUN apt-get install -y \
      curl \
      wget \
      gnupg 

RUN mkdir -p /home/app/
WORKDIR /home/app/

RUN pip install --upgrade pip

# Copy init file executable
COPY entry_point.sh .
RUN chmod u+x entry_point.sh

# install the Pypi package of the project 
# Configure pip
RUN sleep 60;
RUN pip config set global.index-url "https://pypi.org/simple/"


RUN pip install ${PIP_PACKAGE_NAME}==${VERSION}

ENTRYPOINT ["./entry_point.sh"]