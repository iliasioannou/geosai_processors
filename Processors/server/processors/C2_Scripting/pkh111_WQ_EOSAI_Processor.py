#
# 12/01/2018 - v1.0 with TEM,SAL,CUR,DOX products, with some further fixes
#              TO DO: SWH and special forecast coverage 
#
# 11/01/2018 - First release with TEM,SAL,CUR products
#

#
import os
import sys
import subprocess
import time
import gdal
import glob
import datetime
import scipy.io.netcdf as nc
import logging
from sys import platform as _platform
from shutil import copy

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
    snap="C:/Program Files/snap/bin/gpt.exe"
    main_dir="C:/pkh111_EOSAI/"
##Relative folder tree
ancil_dir=main_dir+"C1_Ancillari/"
script_dir=main_dir+"C2_Scripting/"
input_dir=main_dir+"C3_Input/"
temp_dir=main_dir+"C4_TempDir/"
global_output_dir=main_dir+"C5_OutputDir/"

###EOSAI related 
#Naming of input files
TEM_input_f='sv03-med-ingv-tem-an-fc-d'
SAL_input_f='sv03-med-ingv-sal-an-fc-d'
CUR_input_f='sv03-med-ingv-cur-an-fc-d'
DOX_input_f='sv03-med-ogs-bio-an-fc-d'
SWH_input_f='sv03-med-hcmr-wav-an-fc-h'

GPT_006_013_Graph=script_dir+"006_013_Graph_EOSAI.xml"
GPT_006_014_Graph=script_dir+"006_014_Graph_EOSAI.xml"
GPT_006_011_Graph=script_dir+"006_011_Graph_EOSAI.xml"

pFilenames=['TEM','SAL','CUR','DOX','SWH']
Mask_LandSea = [ancil_dir + "Mask_Sea-Land_SRTM_EOSAI.tif"]
AOI_Name = [''] ##['EOSAI_']
ForecastDays=3

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
## Chain_006_013
##
## Processing of products from MEDSEA_ANALYSIS_FORECAST_PHY_006_013
## 
## inputlist: list of files to (singularly) process
## overwrite: 1 = overwrite products if already existing: NO MORE APPLICABLE
## AOI: 1 = EOSAI
## output_dir: it must contain a date at the end of the name and it will be compared with the one inside the input product
## productT: 1==TEM, 2==SAL, 3==CUR
## 
def Chain_006_013(inputlist,overwrite,AOI,output_dir,productT):

    if productT<1 or productT>3:
        logging.info("[EOSAI_PROCESSORS] Wrong 006_013 product variable name: use TEM or SAL or CUR")
        productT=1
        
    #Set specific product internal index
    if productT==1: #TEM
        iin=0
        namevar='thetao'
        namevar2=''
        nameband='thetao'
        nameband2=''
    elif productT==2:  #SAL
        iin=1
        namevar='so'
        namevar2=''
        nameband='so'
        nameband2=''
    elif productT==3: #CUR
        iin=2
        namevar='uo'
        namevar2='vo'
        nameband='inten'
        nameband2='direz'

    # Checks AOI
    if (AOI != 1):
        logging.info("[EOSAI_PROCESSORS] Wrong AOI parameter, set to EOSAI by default.")
        AOI = 1
    AOI = AOI - 1

    logging.info("[EOSAI_PROCESSORS] Selected parameter: "+pFilenames[iin])
    
    #
    # GPT Processing of each single data (in EOSAI it will be always a single one)
    #

    #Creates ad hoc GPT .xml for processing the pre-defined number of (forecast) days
    totlines=[]
    if productT==3: #CURRENT IS PARTICULAR SINCE IT COMBINES TWO BANDS AND GENERATES TWO BANDS
        for n in range(0,ForecastDays+1):
            toaddlines=["        <targetBand>\n",
                        "          <name>"+nameband+"_time"+str(n+1)+"</name>\n",
                        "          <type>float32</type>\n",
                        "          <expression>if ($sourceProduct2.band_1) == 0 then 998 else "+
                        "if ("+namevar+"_time"+str(n+1)+") == 999 then 999 else "+
                        "sqrt(sq("+namevar+"_time"+str(n+1)+")+sq("+namevar2+"_time"+str(n+1)+"))</expression>\n",
                        "          <description/>\n",
                        "          <unit/>\n",
                        "          <noDataValue>999</noDataValue>\n",
                        "        </targetBand>\n"]
            
            toaddlines2=["        <targetBand>\n",
                        "          <name>"+nameband2+"_time"+str(n+1)+"</name>\n",
                        "          <type>float32</type>\n",
                        "          <expression>if ($sourceProduct2.band_1) == 0 then 998 else "+
                        "if ("+namevar+"_time"+str(n+1)+") == 999 then 999 else "+
                        "(180/PI)*atan2("+namevar+"_time"+str(n+1)+","+namevar2+"_time"+str(n+1)+")</expression>\n",
                        "          <description/>\n",
                        "          <unit/>\n",
                        "          <noDataValue>999</noDataValue>\n",
                        "        </targetBand>\n"]

            totlines=totlines+toaddlines+toaddlines2         
    else:
        for n in range(0,ForecastDays+1):
            toaddlines=["        <targetBand>\n",
                        "          <name>"+nameband+"_time"+str(n+1)+"</name>\n",
                        "          <type>float32</type>\n",
                        "          <expression>if ($sourceProduct2.band_1) == 0 then 998 else "+namevar+'_time'+str(n+1)+"</expression>\n",
                        "          <description/>\n",
                        "          <unit/>\n",
                        "          <noDataValue>999</noDataValue>\n",
                        "        </targetBand>\n"]
            totlines=totlines+toaddlines
    
    if os.path.exists(GPT_006_013_Graph)==False:
        logging.debug("[EOSAI_PROCESSORS] GPT template file missing !")
        return 1
        
    fi = open(GPT_006_013_Graph,'r')
    lines=fi.readlines()
    fi.close()
    newlines=lines[0:lines.index('$bandsfill$\n')]
    newlines=newlines+totlines
    newlines=newlines+lines[lines.index('$bandsfill$\n')+1:]
    try:
        GPT_tmp=temp_dir+'006-013_GPT_tmp.xml'
        fo = open(GPT_tmp,'w')
        fo.writelines(newlines)
        fo.close()
    except IOError as e:
        logging.debug("I/O error("+str(e.errno)+") in creating new XML: "+e.strerror)
        return 1
    
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
            dated_filenames.append(pFilenames[iin]+'_'+AOI_Name[AOI]+str(dt.year)+me+da)

        #Check if the corresponding output files have been already generated. If yes simply skip production
        if overwrite==0:
            esistono=0
            for ilday in range(0,ForecastDays+1):
                if os.path.exists(output_dir+dated_filenames[ilday]+'.tif')==True:
                    esistono=esistono+1
            if esistono-1==ForecastDays:
                logging.debug("[EOSAI_PROCESSORS] Products for "+verifdate+" already processed !")
                continue      

        ##############
        ##Parameter  pre-processing
        #

        # Processing with SNAP
        commando=[snap,'-e',GPT_tmp,'-Pfilein='+input_dir+filename,
                       '-Pmaskin='+Mask_LandSea[AOI],
                       '-Pfileout='+temp_dir+filename[:-3]+'.tif',
                       '-Pformat=GeoTIFF+XML']
        try:
            erro=0
            subprocess.check_call(commando)
        except subprocess.CalledProcessError:
            erro=1

        if (erro==1) or os.path.exists(temp_dir+filename[:-3]+'.tif')==None:
            if os.path.isfile(temp_dir+filename[:-3]+'.tif') == True: os.remove(temp_dir+filename[:-3]+'.tif')
            if os.path.isfile(temp_dir+filename[:-3]+'.xml') == True: os.remove(temp_dir+filename[:-3]+'.xml')
            #If GPT fails report it, but continues to next file
            logging.debug("[EOSAI_PROCESSORS] Error in pre-processing "+filename)
            errore=errore+1
            continue

        ######################
        ##Parameter  processing
        #

        for ilday in range(0,ForecastDays+1):
            try:
                data=gdal.Open(temp_dir+filename[:-3]+".tif")
                if productT==3:
                    band=data.GetRasterBand(ilday*2+1)
                    band2=data.GetRasterBand(ilday*2+2)
                else:
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

            # Create the output files
            try:
                outdriver = gdal.GetDriverByName("GTiff")
                if productT==3:
                    outdata   = outdriver.Create(output_dir+dated_filenames[ilday]+'.tif', rows, cols, 2, gdal.GDT_Float32,GDAL_TIFF_Options_list)
                else:
                    outdata   = outdriver.Create(output_dir+dated_filenames[ilday]+'.tif', rows, cols, 1, gdal.GDT_Float32,GDAL_TIFF_Options_list)

                arr=band.ReadAsArray()
                if productT==3: arr2=band2.ReadAsArray()
                
                outdata.GetRasterBand(1).WriteArray(arr)
                if productT==3: outdata.GetRasterBand(2).WriteArray(arr2)
                outdata.SetGeoTransform(trans)
                outdata.SetProjection(proj)
                outdata=None
                arr=None
                arr2=None
                band=None
                band2=None
            except RuntimeError, e:
                #If not generated, still continue
                logging.debug("[EOSAI_PROCESSORS] Error in writing geophysical file "+dated_filenames[ilday]+'.tif')
                errore=errore+1
            ##else:
                #No legend to be applied

            data=None
            
        #Delete intermediate files
        try:
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
                os.remove(temp_dir+filename[:-3]+".xml")
        except:
            a=1
        continue

    if os.path.exists(GPT_tmp): os.remove(GPT_tmp)
    
    if (errore>0):
        return 1

    return 0

########
## Chain_006_014
##
## Processing of products from MEDSEA_ANALYSIS_FORECAST_BIO_006_014
## 
## inputlist: list of files to (singularly) process
## overwrite: 1 = overwrite products if already existing: NO MORE APPLICABLE
## AOI: 1 = EOSAI
## output_dir: it must contain a date at the end of the name and it will be compared with the one inside the input product
## productT: 1==DOX
## 
def Chain_006_014(inputlist,overwrite,AOI,output_dir,productT):

    if productT!=1:
        logging.info("[EOSAI_PROCESSORS] Wrong 006_014 product variable name: use DOX")
        productT=1
        
    #Set specific product internal index
    if productT==1: #DOX
        iin=3
        namevar='dox'
        nameband='dox'
        
    # Checks AOI
    if (AOI != 1):
        logging.info("[EOSAI_PROCESSORS] Wrong AOI parameter, set to EOSAI by default.")
        AOI = 1
    AOI = AOI - 1

    logging.info("[EOSAI_PROCESSORS] Selected parameter: "+pFilenames[iin])
    
    #
    # GPT Processing of each single data (in EOSAI it will be always a single one)
    #

    #Creates ad hoc GPT .xml for processing the pre-defined number of (forecast) days
    totlines=[]
    if productT==1:
        for n in range(0,ForecastDays+1):
            toaddlines=["        <targetBand>\n",
                        "          <name>"+nameband+"_time"+str(n+1)+"</name>\n",
                        "          <type>float32</type>\n",
                        "          <expression>if ($sourceProduct2.band_1) == 0 then 998 else "+namevar+'_time'+str(n+1)+"</expression>\n",
                        "          <description/>\n",
                        "          <unit/>\n",
                        "          <noDataValue>999</noDataValue>\n",
                        "        </targetBand>\n"]
            totlines=totlines+toaddlines
    
    if os.path.exists(GPT_006_014_Graph)==False:
        logging.debug("[EOSAI_PROCESSORS] GPT template file missing !")
        return 1
        
    fi = open(GPT_006_014_Graph,'r')
    lines=fi.readlines()
    fi.close()
    newlines=lines[0:lines.index('$bandsfill$\n')]
    newlines=newlines+totlines
    newlines=newlines+lines[lines.index('$bandsfill$\n')+1:]
    try:
        GPT_tmp=temp_dir+'006-014_GPT_tmp.xml'
        fo = open(GPT_tmp,'w')
        fo.writelines(newlines)
        fo.close()
    except IOError as e:
        logging.debug("I/O error("+str(e.errno)+") in creating new XML: "+e.strerror)
        return 1
    
    errore=0
    for n in range(0,len(inputlist)):
        filename=os.path.basename(inputlist[n])

        if (len(filename) == 0):
            logging.debug("[EOSAI_PROCESSORS] Wrong filename for DOX input "+input_dir+filename)
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
            dated_filenames.append(pFilenames[iin]+'_'+AOI_Name[AOI]+str(dt.year)+me+da)

        #Check if the corresponding output files have been already generated. If yes simply skip production
        if overwrite==0:
            esistono=0
            for ilday in range(0,ForecastDays+1):
                if os.path.exists(output_dir+dated_filenames[ilday]+'.tif')==True:
                    esistono=esistono+1
            if esistono-1==ForecastDays:
                logging.debug("[EOSAI_PROCESSORS] Products for "+verifdate+" already processed !")
                continue      

        ##############
        ##Parameter  pre-processing
        #

        # Processing with SNAP
        commando=[snap,'-e',GPT_tmp,'-Pfilein='+input_dir+filename,
                       '-Pmaskin='+Mask_LandSea[AOI],
                       '-Pfileout='+temp_dir+filename[:-3]+'.tif',
                       '-Pformat=GeoTIFF+XML']
        try:
            erro=0
            subprocess.check_call(commando)
        except subprocess.CalledProcessError:
            erro=1

        if (erro==1) or os.path.exists(temp_dir+filename[:-3]+'.tif')==None:
            if os.path.isfile(temp_dir+filename[:-3]+'.tif') == True: os.remove(temp_dir+filename[:-3]+'.tif')
            if os.path.isfile(temp_dir+filename[:-3]+'.xml') == True: os.remove(temp_dir+filename[:-3]+'.xml')
            #If GPT fails report it, but continues to next file
            logging.debug("[EOSAI_PROCESSORS] Error in pre-processing "+filename)
            errore=errore+1
            continue
        
        ######################
        ##Parameter  processing
        #

        for ilday in range(0,ForecastDays+1):
            try:
                data=gdal.Open(temp_dir+filename[:-3]+".tif")
                if productT==1:
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

            # Create the output files
            try:
                outdriver = gdal.GetDriverByName("GTiff")
                if productT==1:
                    outdata   = outdriver.Create(output_dir+dated_filenames[ilday]+'.tif', rows, cols, 1, gdal.GDT_Float32,GDAL_TIFF_Options_list)

                arr=band.ReadAsArray()
                
                outdata.GetRasterBand(1).WriteArray(arr)
                outdata.SetGeoTransform(trans)
                outdata.SetProjection(proj)
                outdata=None
                arr=None
                arr2=None
                band=None
                band2=None
            except RuntimeError, e:
                #If not generated, still continue
                logging.debug("[EOSAI_PROCESSORS] Error in writing geophysical file "+dated_filenames[ilday]+'.tif')
                errore=errore+1
            ##else:
                #No legend to be applied

            data=None
            
        #Delete intermediate files
        try:
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
                os.remove(temp_dir+filename[:-3]+".xml")
        except:
            a=1
        continue

    if os.path.exists(GPT_tmp): os.remove(GPT_tmp)
    
    if (errore>0):
        return 1

    return 0

########
## Chain_006_011
##
## Processing of products from MEDSEA_ANALYSIS_FORECAST_WAV_006_011
## 
## inputlist: list of files to (singularly) process
## overwrite: 1 = overwrite products if already existing: NO MORE APPLICABLE
## AOI: 1 = EOSAI
## output_dir: it must contain a date at the end of the name and it will be compared with the one inside the input product
## productT: 1==SWH
## 
def Chain_006_011(inputlist,overwrite,AOI,output_dir,productT):

    if productT!=1:
        logging.info("[EOSAI_PROCESSORS] Wrong 006_011 product variable name: use SWH")
        productT=1
        
    #Set specific product internal index
    if productT==1: #SWH
        iin=4
        namevar='VHM0'
        nameband='swh'
        
    # Checks AOI
    if (AOI != 1):
        logging.info("[EOSAI_PROCESSORS] Wrong AOI parameter, set to EOSAI by default.")
        AOI = 1
    AOI = AOI - 1

    logging.info("[EOSAI_PROCESSORS] Selected parameter: "+pFilenames[iin])
    
    #
    # GPT Processing of each single data (in EOSAI it will be always a single one)
    #

    #Creates ad hoc GPT .xml for processing the pre-defined number of (forecast) days
    totlines=[]
    if productT==1:
        for n in range(0,ForecastDays+1):
            formula=''
            for g in range(n*24,n*24+24):
                formula=formula+namevar+'_time'+str(g+1)+'+'
            formula="("+formula[:-1]+")/24"
            toaddlines=["        <targetBand>\n",
                        "          <name>"+nameband+"_time"+str(n+1)+"</name>\n",
                        "          <type>float32</type>\n",
                        "          <expression>if ($sourceProduct2.band_1) == 0 then 998 else "+formula+"</expression>\n",
                        "          <description/>\n",
                        "          <unit/>\n",
                        "          <noDataValue>NaN</noDataValue>\n",
                        "        </targetBand>\n"]
            totlines=totlines+toaddlines
    
    if os.path.exists(GPT_006_011_Graph)==False:
        logging.debug("[EOSAI_PROCESSORS] GPT template file missing !")
        return 1
        
    fi = open(GPT_006_011_Graph,'r')
    lines=fi.readlines()
    fi.close()
    newlines=lines[0:lines.index('$bandsfill$\n')]
    newlines=newlines+totlines
    newlines=newlines+lines[lines.index('$bandsfill$\n')+1:]
    try:
        GPT_tmp=temp_dir+'006-011_GPT_tmp.xml'
        fo = open(GPT_tmp,'w')
        fo.writelines(newlines)
        fo.close()
    except IOError as e:
        logging.debug("I/O error("+str(e.errno)+") in creating new XML: "+e.strerror)
        return 1

    errore=0
    for n in range(0,len(inputlist)):
        filename=os.path.basename(inputlist[n])

        if (len(filename) == 0):
            logging.debug("[EOSAI_PROCESSORS] Wrong filename for SWH input "+input_dir+filename)
            errore=errore+1
            continue

        # Verification of date and definition of final filename taking acquisition date from .nc metadata
        time_min = nc.netcdf_file(input_dir+filename, 'r').time_min
        time_max = nc.netcdf_file(input_dir+filename, 'r').time_max
                            
        t0 = datetime.datetime(1970, 1, 1, 12, 0, 0)
        dt = t0 + datetime.timedelta(hours=time_min)
        dt_max = t0 + datetime.timedelta(hours=time_max)
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
        for latime in range(int(time_min),int(time_max)+1,24):
            dt=t0 + datetime.timedelta(hours=latime)
            me=str(dt.month)
            da=str(dt.day)
            if len(me)==1: me='0'+me
            if len(da)==1: da='0'+da
            dated_filenames.append(pFilenames[iin]+'_'+AOI_Name[AOI]+str(dt.year)+me+da)

        #Check if the corresponding output files have been already generated. If yes simply skip production
        if overwrite==0:
            esistono=0
            for ilday in range(0,ForecastDays+1):
                if os.path.exists(output_dir+dated_filenames[ilday]+'.tif')==True:
                    esistono=esistono+1
            if esistono-1==ForecastDays:
                logging.debug("[EOSAI_PROCESSORS] Products for "+verifdate+" already processed !")
                continue      

        ##############
        ##Parameter  pre-processing
        #

        # Processing with SNAP
        commando=[snap,'-e',GPT_tmp,'-Pfilein='+input_dir+filename,
                       '-Pmaskin='+Mask_LandSea[AOI],
                       '-Pfileout='+temp_dir+filename[:-3]+'.tif',
                       '-Pformat=GeoTIFF+XML']
        try:
            erro=0
            subprocess.check_call(commando)
        except subprocess.CalledProcessError:
            erro=1

        if (erro==1) or os.path.exists(temp_dir+filename[:-3]+'.tif')==None:
            if os.path.isfile(temp_dir+filename[:-3]+'.tif') == True: os.remove(temp_dir+filename[:-3]+'.tif')
            if os.path.isfile(temp_dir+filename[:-3]+'.xml') == True: os.remove(temp_dir+filename[:-3]+'.xml')
            #If GPT fails report it, but continues to next file
            logging.debug("[EOSAI_PROCESSORS] Error in pre-processing "+filename)
            errore=errore+1
            continue
        
        ######################
        ##Parameter  processing
        #

        for ilday in range(0,ForecastDays+1):
            try:
                data=gdal.Open(temp_dir+filename[:-3]+".tif")
                if productT==1:
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

            # Create the output files
            try:
                outdriver = gdal.GetDriverByName("GTiff")
                outdata   = outdriver.Create(output_dir+dated_filenames[ilday]+'.tif', rows, cols, 1, gdal.GDT_Float32,GDAL_TIFF_Options_list)

                arr=band.ReadAsArray()
                outdata.GetRasterBand(1).WriteArray(arr)
                outdata.SetGeoTransform(trans)
                outdata.SetProjection(proj)
                outdata=None
                arr=None
                arr2=None
                band=None
                band2=None
            except RuntimeError, e:
                #If not generated, still continue
                logging.debug("[EOSAI_PROCESSORS] Error in writing geophyisical file "+dated_filenames[ilday]+'.tif')
                errore=errore+1
            ##else:
                #No legend to be applied

            data=None
            
        #Delete intermediate files
        try:
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
                os.remove(temp_dir+filename[:-3]+".xml")
        except:
            a=1
        continue

    if os.path.exists(GPT_tmp): os.remove(GPT_tmp)
    
    if (errore>0):
        return 1

    return 0

############ --------MAIN PROCEDURE ------------------
##########
## WQ_EOSAI_Chain
##
## Input:
##   onflag: bit 0 -> TEM
##           bit 1 -> SAL
##           bit 2 -> CUR
##           bit 3 -> DOX
##           bit 4 -> SWH
##   ovrwflag: Same bit order of onflag. When set to 1, it activates overwriting of already existing products.
##   date: date to be processed (YYYY-MM-DD), which will be the output folder subdir
##   final_folder: optional folder location (ending with '/') where to put the final products when correctly generated,
##                 subfolders TEM,SAL,CUR,DOX and SWH must exist there
##   yesno_folder: optional folder location (ending with '/') where to put a .txt file for the successful generation of
##                 a given product, named ok_XXX_YYYYMMDD.txt
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
        yesno_folder,
        setAOI=[1]):
   
    dest_dir = "%s/" %os.path.join(global_output_dir, date)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    for areaofi in setAOI:
        if len(AOI_Name[areaofi-1])!=0: logging.info("[EOSAI_PROCESSORS] Processing AOI: "+AOI_Name[areaofi-1])
        
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
                result1=Chain_006_013(ce,ovrw,areaofi,dest_dir,1)
                if result1==1:
                    logging.debug("[EOSAI_PROCESSORS] "+'Failed generation of TEM products for date: '+date)
                    eerr=1
                else:
                    #Copy products
                    copyerror=0
                    if len(final_folder)!=0:
                        ce=glob.glob(dest_dir+'TEM_*.tif')
                        if len(ce)!=ForecastDays+1:
                            logging.debug("[EOSAI_PROCESSORS] "+'Generated TEM products not as expected for date: '+date)
                            copyerror=1
                        else:
                            mverror=0
                            for cefil in ce:
                                try:
                                    if os.path.exists(final_folder+'/TEM/'+os.path.basename(cefil))==True:
                                        os.remove(final_folder+'/TEM/'+os.path.basename(cefil))
                                except Exception, e:
                                    mverror=mverror+1
                                    logging.error('error during TEM erasing: '+ str(e))
                                else:
                                    try:
                                        copy(cefil,final_folder+'/TEM/'+os.path.basename(cefil))
                                    except Exception, e:
                                        mverror=mverror+1
                                        logging.error('error during TEM erasing: '+ str(e))
                            if mverror!=0:
                                logging.debug("[EOSAI_PROCESSORS] "+'Failed in copying '+str(mverror)+' TEM products for date: '+date)
                                if mverror==(ForecastDays+1):
                                    copyerror=1
                    #Write yesno logfile
                    if len(yesno_folder)!=0 and copyerror==0:
                        try:
                            fo = open(yesno_folder+"ok_TEM_"+date.replace('-','')+'.txt','w')
                            fo.write("Generated TEM products for "+date+"\n")
                            fo.close()
                        except IOError as e:
                            logging.debug("I/O error("+str(e.errno)+") in writing TEM yesno logfile: "+e.strerror)

        ###SAL section
        if (onflag & 2)!=0:
            ovrw=0
            if (ovrwflag & 2)!=0: ovrw=1    
            #Search for SAL input files
            ce=glob.glob(input_dir+SAL_input_f+'*'+date+'.nc')
            if len(ce)==0:
                logging.debug("[EOSAI_PROCESSORS] "+'No SAL input files to process with specified date: '+date)
            else:
                result1=Chain_006_013(ce,ovrw,areaofi,dest_dir,2)
                if result1==1:
                    logging.debug("[EOSAI_PROCESSORS] "+'Failed generation of SAL products for date: '+date)
                    eerr=1
                else:
                    #Copy products
                    copyerror=0
                    if len(final_folder)!=0:
                        ce=glob.glob(dest_dir+'SAL_*.tif')
                        if len(ce)!=ForecastDays+1:
                            logging.debug("[EOSAI_PROCESSORS] "+'Generated SAL products not as expected for date: '+date)
                            copyerror=1
                        else:
                            mverror=0
                            for cefil in ce:
                                try:
                                    if os.path.exists(final_folder+'/SAL/'+os.path.basename(cefil))==True:
                                        os.remove(final_folder+'/SAL/'+os.path.basename(cefil))
                                except:
                                    mverror=mverror+1
                                else:
                                    try:
                                        copy(cefil,final_folder+'/SAL/'+os.path.basename(cefil))
                                    except:
                                        mverror=mverror+1
                            if mverror!=0:
                                logging.debug("[EOSAI_PROCESSORS] "+'Failed in copying '+str(mverror)+' SAL products for date: '+date)
                                if mverror==(ForecastDays+1):
                                    copyerror=1
                    #Write yesno logfile
                    if len(yesno_folder)!=0 and copyerror==0:
                        try:
                            fo = open(yesno_folder+"ok_SAL_"+date.replace('-','')+'.txt','w')
                            fo.write("Generated SAL products for "+date+"\n")
                            fo.close()
                        except IOError as e:
                            logging.debug("I/O error("+str(e.errno)+") in writing SAL yesno logfile: "+e.strerror)

        ###CUR section
        if (onflag & 4)!=0:
            ovrw=0
            if (ovrwflag & 4)!=0: ovrw=1    
            #Search for CUR input files
            ce=glob.glob(input_dir+CUR_input_f+'*'+date+'.nc')
            if len(ce)==0:
                logging.debug("[EOSAI_PROCESSORS] "+'No CUR input files to process with specified date: '+date)
            else:
                result1=Chain_006_013(ce,ovrw,areaofi,dest_dir,3)
                if result1==1:
                    logging.debug("[EOSAI_PROCESSORS] "+'Failed generation of CUR proucts for date: '+date)
                    eerr=1
                else:
                    #Copy products
                    copyerror=0
                    if len(final_folder)!=0:
                        ce=glob.glob(dest_dir+'CUR_*.tif')
                        if len(ce)!=ForecastDays+1:
                            logging.debug("[EOSAI_PROCESSORS] "+'Generated CUR products not as expected for date: '+date)
                            copyerror=1
                        else:
                            mverror=0
                            for cefil in ce:
                                try:
                                    if os.path.exists(final_folder+'/CUR/'+os.path.basename(cefil))==True:
                                        os.remove(final_folder+'/CUR/'+os.path.basename(cefil))
                                except:
                                    mverror=mverror+1
                                else:
                                    try:
                                        copy(cefil,final_folder+'/CUR/'+os.path.basename(cefil))
                                    except:
                                        mverror=mverror+1
                            if mverror!=0:
                                logging.debug("[EOSAI_PROCESSORS] "+'Failed in copying '+str(mverror)+' SAL products for date: '+date)
                                if mverror==(ForecastDays+1):
                                    copyerror=1
                    #Write yesno logfile
                    if len(yesno_folder)!=0 and copyerror==0:
                        try:
                            fo = open(yesno_folder+"ok_CUR_"+date.replace('-','')+'.txt','w')
                            fo.write("Generated CUR products for "+date+"\n")
                            fo.close()
                        except IOError as e:
                            logging.debug("I/O error("+str(e.errno)+") in writing CUR yesno logfile: "+e.strerror)
        ###DOX section
        if (onflag & 8)!=0:
            ovrw=0
            if (ovrwflag & 8)!=0: ovrw=1    
            #Search for DOX input files
            ce=glob.glob(input_dir+DOX_input_f+'*'+date+'.nc')
            if len(ce)==0:
                logging.debug("[EOSAI_PROCESSORS] "+'No DOX input files to process with specified date: '+date)
            else:
                result1=Chain_006_014(ce,ovrw,areaofi,dest_dir,1)
                if result1==1:
                    logging.debug("[EOSAI_PROCESSORS] "+'Failed generation of DOX products for date: '+date)
                    eerr=1
                else:
                    #Copy products
                    copyerror=0
                    if len(final_folder)!=0:
                        ce=glob.glob(dest_dir+'DOX_*.tif')
                        if len(ce)!=ForecastDays+1:
                            logging.debug("[EOSAI_PROCESSORS] "+'Generated DOX products not as expected for date: '+date)
                            copyerror=1
                        else:
                            mverror=0
                            for cefil in ce:
                                try:
                                    if os.path.exists(final_folder+'/DOX/'+os.path.basename(cefil))==True:
                                        os.remove(final_folder+'/DOX/'+os.path.basename(cefil))
                                except:
                                    mverror=mverror+1
                                else:
                                    try:
                                        copy(cefil,final_folder+'/DOX/'+os.path.basename(cefil))
                                    except:
                                        mverror=mverror+1
                            if mverror!=0:
                                logging.debug("[EOSAI_PROCESSORS] "+'Failed in copying '+str(mverror)+' DOX products for date: '+date)
                                if mverror==(ForecastDays+1):
                                    copyerror=1
                    #Write yesno logfile
                    if len(yesno_folder)!=0 and copyerror==0:
                        try:
                            fo = open(yesno_folder+"ok_DOX_"+date.replace('-','')+'.txt','w')
                            fo.write("Generated DOX products for "+date+"\n")
                            fo.close()
                        except IOError as e:
                            logging.debug("I/O error("+str(e.errno)+") in writing DOX yesno logfile: "+e.strerror)

        ###SWH section
        if (onflag & 16)!=0:
            ovrw=0
            if (ovrwflag & 16)!=0: ovrw=1    
            #Search for SWH input files
            ce=glob.glob(input_dir+SWH_input_f+'*'+date+'.nc')
            if len(ce)==0:
                logging.debug("[EOSAI_PROCESSORS] "+'No SWH input files to process with specified date: '+date)
            else:
                result1=Chain_006_011(ce,ovrw,areaofi,dest_dir,1)
                if result1==1:
                    logging.debug("[EOSAI_PROCESSORS] "+'Failed generation of SWH proucts for date: '+date)
                    eerr=1
                else:
                    #Copy products
                    copyerror=0
                    if len(final_folder)!=0:
                        ce=glob.glob(dest_dir+'SWH_*.tif')
                        if len(ce)!=ForecastDays+1:
                            logging.debug("[EOSAI_PROCESSORS] "+'Generated SWH products not as expected for date: '+date)
                            copyerror=1
                        else:
                            mverror=0
                            for cefil in ce:
                                try:
                                    if os.path.exists(final_folder+'/SWH/'+os.path.basename(cefil))==True:
                                        os.remove(final_folder+'/SWH/'+os.path.basename(cefil))
                                except:
                                    mverror=mverror+1
                                else:
                                    try:
                                        copy(cefil,final_folder+'/SWH/'+os.path.basename(cefil))
                                    except:
                                        mverror=mverror+1
                            if mverror!=0:
                                logging.debug("[EOSAI_PROCESSORS] "+'Failed in copying '+str(mverror)+' SWH products for date: '+date)
                                if mverror==(ForecastDays+1):
                                    copyerror=1
                    #Write yesno logfile
                    if len(yesno_folder)!=0 and copyerror==0:
                        try:
                            fo = open(yesno_folder+"ok_SWH_"+date.replace('-','')+'.txt','w')
                            fo.write("Generated SWH products for "+date+"\n")
                            fo.close()
                        except IOError as e:
                            logging.debug("I/O error("+str(e.errno)+") in writing SWH yesno logfile: "+e.strerror)
    if eerr==1: return 1

    return 0

if __name__ == '__main__':
##
##Manual testing
    logging.info("Main body.")

    res=WQ_EOSAI_Chain(15,15,'2018-01-10',global_output_dir,global_output_dir)
    res=WQ_EOSAI_Chain(15,15,'2018-01-11',global_output_dir,global_output_dir)  
                                        
    print res

    logging.info("Ended.")
