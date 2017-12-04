#! /bin/bash

cd base
docker build -t dockerhub.planetek.it/pkh111_eosai_processors:base .
docker push dockerhub.planetek.it/pkh111_eosai_processors:master

cd ..
docker build --no-cache -t dockerhub.planetek.it/pkh111_eosai_processors:$1 --build-arg branch=$1 .
docker push dockerhub.planetek.it/pkh111_eosai_processors:$1