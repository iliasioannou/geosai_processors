#! /bin/bash

cd base
docker build -t planetek/cmems_processors:base .

cd ..
docker build --no-cache -t planetek/cmems_processors:$1 --build-arg branch=$1 .
