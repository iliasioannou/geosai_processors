FROM ubuntu:xenial

WORKDIR /home

#REMEMBER: better to separate the update command
RUN apt-get -qq -y update \
          && apt-get --yes install libwxgtk3.0-dev libgdal-dev libproj-dev libjasper-dev libexpat1-dev wx-common libexpat1-dev libogdi3.2-dev unixodbc-dev \
		  && apt-get -y install libtiff5-dev \
		  && apt-get -y install g++ make automake libtool git

#To install wget command
RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*		  

#### SAGA Gis 3.0.0 installation (by compiling)
RUN wget https://sourceforge.net/projects/saga-gis/files/SAGA%20-%203/SAGA%20-%203.0.0/saga_3.0.0.tar.gz/download -O /home/saga_3.0.0.tar.gz
RUN tar xvzf /home/saga_3.0.0.tar.gz

RUN cd saga-3.0.0 && autoreconf -i && ./configure && make && make install && echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc 
RUN export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

#### SNAP 5.0 installation
#Installation set to /opt/snap.
RUN wget http://step.esa.int/downloads/5.0/installers/esa-snap_all_unix_5_0.sh -O /home/esa-snap_all_unix_5_0.sh
RUN chmod 777 /home/esa-snap_all_unix_5_0.sh
ADD /installers/response.varfile /home

RUN ./esa-snap_all_unix_5_0.sh -q -varfile response.varfile && snap --nosplash --nogui --modules --update-all

#### ANACONDA 4.3.0 64bit installation with needed python packages
RUN wget https://repo.continuum.io/archive/Anaconda2-4.3.0-Linux-x86_64.sh -O /home/Anaconda2-4.3.0-Linux-x86_64.sh
RUN chmod 777 /home/Anaconda2-4.3.0-Linux-x86_64.sh

RUN bash ./Anaconda2-4.3.0-Linux-x86_64.sh -b -p ./anaconda
RUN echo 'export PATH="/home/anaconda/bin:$PATH"' >> /home/.bashrc
RUN export PATH="/home/anaconda/bin:$PATH" && conda update -y conda && conda install -y gdal
RUN export PATH="/home/anaconda/bin:$PATH" && conda update -y numpy && conda update -y gdal
RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

VOLUME /home/CMEMS

#### READY

#ENTRYPOINT ["/home/anaconda/bin/python2.7","/home/CMEMS/02_Scripting/pkz029_WQ_CMEMS_Processor.py"]