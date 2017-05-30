# Qui vanno inseriti i sorgenti dei processori e del wrapper XML-RPC per lanciarli da remoto

### CMEMS Docker image build&configure
**To create the docker image**
To create the image with the Dockerfile, the *response.varfile* configuration file is needed. 
Furthermore in building the image it will download the following installation files:

a) https://sourceforge.net/projects/saga-gis/files/SAGA%20-%203/SAGA%20-%203.0.0/saga_3.0.0.tar.gz/download (4Mb)

b) http://step.esa.int/downloads/5.0/installers/esa-snap_all_unix_5_0.sh (460Mb)

c) https://repo.continuum.io/archive/Anaconda2-4.3.0-Linux-x86_64.sh (475Mg)

To build the image, launch e.g.
*docker build -t cmems .*

**Configuration**
One host folders needs to be linked (-v option) when running the image to the main folder of the procedure.
This is the completed expected folder tree with the input, intermediate and final output:
- 01_Ancillari: It contains the files in ancillary folder on git
- 02_Scripting: It contains the files in the processors folder on git
- 03_Input
- 04_TempDir
- 05_OutputDir: It will contain the output files (see note below about output location)
### CMEMS Docker image use: daily processor
**How to launch the CMEMS processor with docker:**

docker run -v <host path to main folder>:/home/CMEMS cmems first_argument second_argument process_ID

* first_argument: bit coded intereg (4 bits) to define the products to be generated
    - bit 0 -> sst
    - bit 1 -> chl
    - bit 2 -> wt
    - bit 3 -> tur
* second_argument: same bit order of previous. When set to 1, it activates overwriting of already existing products of the corresponding ptoruct type
* process_ID: string appended to the logfile name

EXAMPLE:
*docker run -v D:\pkz029_CMEMS:/home/CMEMS cmems 3 3 003*

**Input files**
* CHL
- dataset-oc-med-chl-multi-l3-chl_1km_daily-rt*.nc
* SST
SST_MED_SST_L3S_NRT_OBSERVATIONS_010_012_b*.nc
* WT & Tur [**non ancora operativi**]
- dataset-oc-med-opt-multi-l3-kd490_1km_daily-rt*.nc
- dataset-oc-med-opt-multi-l3-rrs490_1km_daily-rt*.nc
dataset-oc-med-opt-multi-l3-rrs555_1km_daily-rt*.nc
dataset-oc-med-opt-multi-l3-rrs670_1km_daily-rt*.nc

**Output files**
The output files should be kept in a defined location in order to allow the procedure which calculates the statistics, to find them.
Output file naming:
RC_aoi_yyyy_mm_dd_prod_type.tif
- aoi = ITA or GRE
- yyyy = year
- mm = month (01-12)
- dd = day (01-31)
- prod = Chl or SST or WT or Tur
- type = Num or Thematic

