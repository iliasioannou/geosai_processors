FROM planetek/cmems_processors:base

ARG branch

RUN git clone -b $branch https://teamEreticoTfs:vAsK*AIJFB@tfs.planetek.it/SBU-GS/pkz029_UU_CMEMS/_git/pkz029_UU_CMEMS_Processori /src

WORKDIR /src/Processors/server
CMD ["/home/anaconda/bin/python2.7","wq_server.py"]
