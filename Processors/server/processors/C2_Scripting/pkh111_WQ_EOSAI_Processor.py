#
# xx/01/2018 
#

#
import os
import sys
import subprocess
import time
import gdal
import glob
import numpy as np
import datetime
import scipy.io.netcdf as nc
import logging
from sys import platform as _platform

############
## Pre-fixed information
##
#General
main_dir="/src/Processors/server/processors/"
##main_dir="/home/EOSAI/"
snap="/opt/snap/bin/gpt"

#FOR DEBUGGING ON WINDOWS
if _platform == "win32":
    sagagis=['C:/Programmis/saga_3.0.0_x64/saga_cmd','-f=s']
    snap="C:/Programmis/snap5/bin/gpt.exe"
    main_dir="D:/pkh111_EOSAI/"
##Relative folder tree
ancil_dir=main_dir+"C1_Ancillari/"
script_dir=main_dir+"C2_Scripting/"
input_dir=main_dir+"C3_Input/"
temp_dir=main_dir+"C4_TempDir/"
global_output_dir=main_dir+"C5_OutputDir/"

###EOSAI related 
TEM_input_f='sv03-med-ingv-tem-an-fc-d'

GPT_TEM_Graph=[script_dir+"TEM4_Graph_EOSAI.xml"]


pFilenames=['TEM','SAL','CUR','DO2','SSW']
Mask_LandSea = [ancil_dir + "Mask_Sea-Land_SRTM_EOSAI.tif"]
AOI_Name = ['EOSAI']
ForecastDays=4

###Others
GDAL_TIFF_Options_list=['COMPRESS=LZW','TILED=YES']

if _platform == "linux" or _platform == "linux2":
    a=1
else:
    ##Only for testing in Windows
    logging.basicConfig(filename=global_output_dir+'thisismy.log',filemode='a',format='[EOSAI] %(asctime)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
###---------------------------------------------------------------------------

########
## TEM_Processing
##
## Processing of TEM EOSAI TEM_MED_TEM_L3S_NRT_OBSERVATIONS_010_012_b
## 
## inputlist: list of files to (singularly) process
## overwrite: 1 = overwrite products if already existing: NO MORE APPLICABLE
## AOI: 1 = EOSAI
## output_dir: it must contain a date in the name and it will be compared with the one inside the input product
## 
def TEM_Chain(inputlist,overwrite,AOI,output_dir):
    
    #TEM product internal index
    iin=3

    # Checks AOI
    if (AOI != 1):
        logging.info("[EOSAI_PROCESSORS] Wrong AOI parameter, set to EOSAI by default.")
        AOI = 1
    AOI = AOI - 1

    logging.info("[EOSAI_PROCESSORS] Selected parameter: TEM")
    #
    # GPT Processing of each single data (in EOSAI it will be always a single one)
    #
    errore=0
    for n in range(0,len(inputlist)):
        filename=os.path.basename(inputlist[n])

        if (len(filename) == 0):
            logging.debug("[EOSAI_PROCESSORS] Wrong filename for TEM input "+input_dir+filename)
            errore=errore+1
            continue

        # Verification of date and definition of final filename taking acquisition date from .nc metadata
        time_min = nc.netcdf_file(input_dir+filename, 'r').time_min
        time_max = nc.netcdf_file(input_dir+filename, 'r').time_max
							
        t0 = datetime.datetime(1970, 1, 1)
        dt = t0 + datetime.timedelta(days=time_min)
        dt_max = t0 + datetime.timedelta(days=time_max)
        me=str(dt.month)
        da=str(dt.day)
        if len(me)==1: me='0'+me
        if len(da)==1: da='0'+da
        verifdate=str(dt.year)+'-'+me+'-'+da
					
        if output_dir.find(verifdate)== -1:
            logging.debug("[EOSAI_PROCESSORS] The date into the product ("+verifdate+") differs from the one of the outputdir("+output_dir+")")
            logging.debug("[EOSAI_PROCESSORS] Product not generated !!")
            continue
        if (time_max-time_min) < ForecastDays:
            logging.debug("[EOSAI_PROCESSORS] The input product has not enough forecast days ("+str(time_max-time_min)+")")
            logging.debug("[EOSAI_PROCESSORS] Product not generated !!")
            continue
        dated_filenames=[]
        for latime in range(int(time_min),int(time_max)+1):
            dt=t0 + datetime.timedelta(days=latime)
            me=str(dt.month)
            da=str(dt.day)
            if len(me)==1: me='0'+me
            if len(da)==1: da='0'+da
            dated_filenames.append(pFilenames[iin]+'_'+AOI_Name[AOI]+'_'+str(dt.year)+me+da)

##            #Check if the corresponding output has been already generated - IT HAS NO SENSE
##            if overwrite==0:
##                if os.path.exists(output_dir+prod_filename_num):
##                    logging.debug("[EOSAI_PROCESSORS] "+dated_filenames+".tif already processed !")
                    

        ##############
        ##TEM  pre-processing
        #

        # Processing with SNAP
        commando=[snap,'-e',GPT_TEM_Graph[AOI],'-Pfilein='+input_dir+filename,
                       '-Pmaskin='+Mask_LandSea[AOI],
                       '-Pfileout='+temp_dir+filename[:-3]+'.tif',
                       '-Pformat=GeoTIFF+XML']
        print commando
        try:
            erro=0
            subprocess.check_call(commando)
        except subprocess.CalledProcessError:
            erro=1

        if (erro==1) or os.path.exists(temp_dir+filename[:-3]+'.tif')==None:
            b=c
            if os.path.isfile(temp_dir+filename[:-3]+'.tif') == True: os.remove(temp_dir+filename[:-3]+'.tif')
            if os.path.isfile(temp_dir+filename[:-3]+'.xml') == True: os.remove(temp_dir+filename[:-3]+'.xml')
            #If GPT fails report it, but continues to next file
            logging.debug("[EOSAI_PROCESSORS] Error in pre-processing "+filename)
            errore=errore+1
            continue

        a=b       
        ######################
        ##TEM  processing
        #

        for ilday in range(0,ForecastDays):

            try:
                data=gdal.Open(temp_dir+filename[:-3]+".tif")
                band=data.GetRasterBand(ilday+1)
                arr=band.ReadAsArray()
            except RuntimeError, e:
                logging.debug("[EOSAI_PROCESSORS] Error in reading day "+str(ilday+1)+" from file "+temp_dir+filename[:-3]+".tif")
                data=None
                errore=errore+1
                if os.path.isfile(temp_dir+filename[:-3]+'.tif') == True: os.remove(temp_dir+filename[:-3]+'.tif')
                if os.path.isfile(temp_dir+filename[:-3]+'.xml') == True: os.remove(temp_dir+filename[:-3]+'.xml')
                continue       

            #Reads info from the generated product       
            [cols,rows] = arr.shape
            trans       = data.GetGeoTransform()
            proj        = data.GetProjection()
            arr=None
            band=None

            # Create the output files
            try:
                outdriver = gdal.GetDriverByName("GTiff")
                outdata   = outdriver.Create(output_dir+prod_filename_num, rows, cols, 1, gdal.GDT_Float32,GDAL_TIFF_Options_list)

                band=data.GetRasterBand(1)
                arr=band.ReadAsArray()
                
                outdata.GetRasterBand(1).WriteArray(arr)
                outdata.SetGeoTransform(trans)
                outdata.SetProjection(proj)
                outdata=None
                arr=None
                band=None
            except RuntimeError, e:
                #If not generated, still continue
                logging.debug("[EOSAI_PROCESSORS] Error in writing geophyisical file "+prod_filename_num)
                errore=errore+1
            ##else:
                #No legend to be applied

            data=None
            
        #Delete intermediate files
        os.remove(temp_dir+filename[:-3]+".tif")
        if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
            os.remove(temp_dir+filename[:-3]+".xml")
        continue
   
    if (errore>0):
        return 1

    return 0

############ --------MAIN PROCEDURE ------------------
##########
## WQ_EOSAI_Chain
##
## Input:
##   onflag: bit 0 -> tem
##           bit 1 -> do2
##           bit 2 -> sal
##           bit 3 -> ssw
##           bit 4 -> cur
##   ovrwflag: same bit order of onflag. When set to 1, it activates overwriting of already existing products
##   date: date to be processed, which will be the output folder subdir
##   final_folder: folder tree where to put the final products when correctly generated
##   setAOI: 1=EOSAI
##   
##
## Output: 0 okay, 1 any error
##
def WQ_EOSAI_Chain(
        onflag,
        ovrwflag,
        date,
        final_folder,
        setAOI=[1]):
   
    dest_dir = "%s/" %os.path.join(global_output_dir, date)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    for areaofi in setAOI:
        logging.info("[EOSAI_PROCESSORS] Processing AOI: "+AOI_Name[areaofi-1])
        
        eerr=0
        ###TEM section
        if (onflag & 1)!=0:
            ovrw=0
            if (ovrwflag & 1)!=0: ovrw=1    
            #Search for TEM input files
            ce=glob.glob(input_dir+TEM_input_f+'*'+date+'.nc')
            if len(ce)==0:
                logging.debug("[EOSAI_PROCESSORS] "+'No TEM input files to process with specified date: '+date)
            else:
                result1=TEM_Chain(ce,ovrw,areaofi, dest_dir)
                if result1==1: eerr=1
    if eerr==1:
        return 1,dest_dir

    return 0,dest_dir

if __name__ == '__main__':
##
##Manual testing
    logging.info("Main body.")

    res=WQ_EOSAI_Chain(15,0,'2018-01-10','')
			   
  
							
										
    print res

    logging.info("Ended.")
