FROM dockerhub.planetek.it/pkh111_eosai_processors:base

ARG branch

RUN git clone -b $branch https://teamEreticoTfs:hIEMK-i=d@tfs.planetek.it/Planetek%20Hellas/pkh111_EOSAI/_git/pkh111_EOSAI_Processori /src

WORKDIR /src/Processors/server
CMD ["/home/anaconda/bin/python2.7","wq_server.py"]
