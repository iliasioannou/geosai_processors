#! /bin/bash

docker build -t planetek/cmems_processors:develop -f base/Dockerfile
docker build --no-cache -t planetek/cmems_processors_complete:$1 --build-arg branch=$1 .