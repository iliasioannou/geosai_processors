# Sorgenti dei processori e del wrapper XML-RPC per lanciarli da remoto

### EOSAI Docker image build&configure

**To create the docker image**
To create the image with the Dockerfile, the *response.varfile* configuration file is needed. 
Furthermore in building the image it will download the following installation files:

a) https://sourceforge.net/projects/saga-gis/files/SAGA%20-%203/SAGA%20-%203.0.0/saga_3.0.0.tar.gz/download (4Mb)

b) http://step.esa.int/downloads/5.0/installers/esa-snap_all_unix_5_0.sh (460Mb)

c) https://repo.continuum.io/archive/Anaconda2-4.3.0-Linux-x86_64.sh (475Mb)

To build the image, launch e.g.
*docker build -t dockerhub.planetek.it/pkh111_eosai .*

**Configuration**
One host folders needs to be linked (-v option) when running the image to the main folder of the procedure.
This is the completed expected folder tree with the input, intermediate and final output:
- C1_Ancillari: It contains the files in ancillary folder on git
- C2_Scripting: It contains the files in the processors folder on git
- C3_Input: It will contain the input files (see below)
- C4_TempDir: It will contain all temporary files, which will be deleted at the end of the process
- C5_OutputDir: It will contain the output files (see note below about output location)
- C6_FinalOutput:

### EOSAI Docker image use: daily processor

List of available Products:
Sea Water Temperature -> TEM
Dissolved Oxygen -> DOX
Salinity -> SAL
Significant Wave Height -> SWH
Currents -> CUR

**How to launch the EOSAI processor with docker:**

docker run -v <host path to main folder>:/home/EOSAI pkh111_eosai first_argument second_argument process_ID

* first_argument: bit coded intereg (5 bits) to define the products to be generated
    - bit 0 -> CUR
    - bit 1 -> DOX
    - bit 2 -> SAL
    - bit 3 -> SWH
    - bit 3 -> TEM

* second_argument: same bit order of previous. When set to 1, it activates overwriting of already existing products of the corresponding ptoruct type
* process_ID: string appended to the logfile name

EXAMPLE:
*docker run -v D:\pkh111_EOSAI:/home/EOSAI eosai 3 3 003*

**Input files**

* MEDSEA_ANALYSIS_FORECAST_BIO_006_014-TDS
    - DOX [dsv03-med-ogs-bio-an-fc-d.nc]
* MEDSEA_ANALYSIS_FORECAST_PHY_006_013-TDS
    - TEM [sv03-med-ingv-tem-an-fc-d]
    - SAL [sv03-med-ingv-sal-an-fc-d]
    - CUR [sv03-med-ingv-cur-an-fc-d]
* MEDSEA_ANALYSIS_FORECAST_WAV_006_017-TDS
    - SWH [sv04-med-hcmr-wav-an-fc-h]
