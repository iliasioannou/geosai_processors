#! /bin/bash

cd base
docker build -t planetek/eosai_processors:base .

cd ..
docker build --no-cache -t planetek/eosai_processors:$1 --build-arg branch=$1 .
