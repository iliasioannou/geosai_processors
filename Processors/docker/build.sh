#! /bin/bash

docker build -t planetek/cmems_processors:base -f base/Dockerfile
docker build --no-cache -t planetek/cmems_processors:$1 --build-arg branch=$1 .