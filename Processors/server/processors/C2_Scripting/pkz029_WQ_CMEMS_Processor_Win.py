#
#
# TO DO:
#
# Open issues:
#        -surface_tempearure or adjusted_surface_temperature
#        -check the use of quality_level for SST (taken in the pre-processing)
#        -gdal on Windows is not able to read NETCDF, so scipy library is needed
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

from pke114_Apply_Legend import Read_Legend ##Need to be in the same folder
from pke114_Apply_Legend import Apply_Legend ##Need to be in the same folder
from pke114_Apply_Legend import RGB_as_input ##Need to be in the same folder


############
## Pre-fixed information
##
#General
main_dir="D:/pkz029_CMEMS/"
snap="C:/Programmis/snap5/bin/gpt"

##Relative folder tree
ancil_dir=main_dir+"C1_Ancillari/"
script_dir=main_dir+"C2_Scripting/"
input_dir=main_dir+"C3_Input/"
temp_dir=main_dir+"C4_TempDir/"
global_output_dir=main_dir+"C5_OutputDir/"

###CMEMS related 
SST_input_f='SST_MED_SST_L3S_NRT_OBSERVATIONS_010_012_b_'
CHL_input_f='dataset-oc-med-chl-multi-l3-chl_1km_daily-rt'
OC_input_f=['dataset-oc-med-opt-multi-l3-rrs490_1km_daily-rt',
            'dataset-oc-med-opt-multi-l3-rrs555_1km_daily-rt',
            'dataset-oc-med-opt-multi-l3-rrs670_1km_daily-rt',
            'dataset-oc-med-opt-multi-l3-kd490_1km_daily-rt']
GPT_Chl_Graph=[script_dir+"Chl_Graph_CMEMS.xml",script_dir+"Chl_Graph_CMEMS_GRE.xml"]
GPT_SST_Graph=[script_dir+"SST_Graph_CMEMS.xml",script_dir+"SST_Graph_CMEMS_GRE.xml"]
GPT_TWT_Graph=[script_dir+"TWT_Graph_CMEMS.xml",script_dir+"TWT_Graph_CMEMS_GRE.xml"]

pFilenames=['Chl','WT','Tur','SST']
Legends=[ancil_dir+'Legenda_CHL.txt',
         ancil_dir+'Legenda_TR.txt',
         ancil_dir+'Legenda_Turb.txt',
         ancil_dir+'Legenda_SST.txt']
Mask_LandSea=[ancil_dir+"Mask_Sea-Land_SRTM_Adriatic.tif",ancil_dir+"Mask_Sea-Land_SRTM_Aegeus.tif"]
AOI_Name=['ITA','GRE']

###Others
GDAL_TIFF_Options_list=['COMPRESS=LZW','TILED=YES']

if _platform == "linux" or _platform == "linux2":
    a=1
else:
    ##Only for testing in Windows
    logging.basicConfig(filename=global_output_dir+'thisismy.log',filemode='w',format='[CMEMS] %(asctime)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
###---------------------------------------------------------------------------

   

########
## SST_Processing
##
## Processing of SST CMEMS SST_MED_SST_L3S_NRT_OBSERVATIONS_010_012_b
##
## inputlist: list of files to (singularly) process
## overwrite: 1 = overwrite products if already existing
## AOI: 1=Italy/Adriatic 2=Greece (any other == Italy)
## output_dir: it must contain a date and it will be compared with the one inside the input product
## 
def SST_Chain(inputlist,overwrite,AOI, output_dir):
    
    #SST product internal index
    iin=3

    #Checks AOI
    if (AOI!=1) and (AOI!=2):
        logging.debug("[CMEMS_PROCESSORS] Wrong AOI parameter, set to Adriatic")
        AOI=1
    AOI=AOI-1

    logging.info("[CMEMS_PROCESSORS] Selected parameter: SST")
    #
    #GPT Processing of each single data (in CMEMS it will be always a single one)
    #
    qualcheerrore=0
    for n in range(0,len(inputlist)):
        filename=os.path.basename(inputlist[n])

        if (len(filename) == 0):
            logging.debug("[CMEMS_PROCESSORS] Wrong filename for SST input "+input_dir+filename)
            qualcheerrore=qualcheerrore+1
            continue

        # Definition of final filename taking acquisition date from .nc metadata
        time = nc.netcdf_file(input_dir+filename, 'r').time_min
        t0 = datetime.datetime(1981, 1, 1)
        dt = t0 + datetime.timedelta(seconds=time)
        me=str(dt.month)
        da=str(dt.day)
        if len(me)==1: me='0'+me
        if len(da)==1: da='0'+da
        verifdate=str(dt.year)+'-'+me+'-'+da
        if output_dir.find(verifdate)== -1:
            logging.debug("[CMEMS_PROCESSORS] The date into the product ("+verifdate+") differs from the one of the outputdir("+output_dir+")")
            logging.debug("[CMEMS_PROCESSORS] Product not generated !!")
            continue
        #dated_filename='RC_'+AOI_Name[AOI]+'_'+str(dt.year)+'_'+me+'_'+da
        dated_filename='RC_'+AOI_Name[AOI]+'_'+str(dt.year)+me+da
        prod_filename_num=dated_filename+"_"+pFilenames[iin]+"_Num.tif"
        prod_filename_the=dated_filename+"_"+pFilenames[iin]+"_Thematic.tif"

        #Check if the corresponding output has been already generated
        if overwrite==0:
            if os.path.exists(output_dir+prod_filename_num) and os.path.exists(output_dir+prod_filename_the):
                logging.debug("[CMEMS_PROCESSORS] "+filename+" already processed !")
                continue
        

        ##############
        ##SST  pre-processing
        #

        # Processing with SNAP
        commando=[snap,'-e',GPT_SST_Graph[AOI],'-Pfilein='+input_dir+filename,
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
            logging.debug("[CMEMS_PROCESSORS] Error in pre-processing "+filename)
            qualcheerrore=qualcheerrore+1
            continue
       
        #Check if there is at least a valid pixels, otherwise delete it
        try:
            data=gdal.Open(temp_dir+filename[:-3]+".tif")
            band=data.GetRasterBand(1)
            arr=band.ReadAsArray()
        except RuntimeError, e:
            logging.debug("[CMEMS_PROCESSORS] Error in reading file "+temp_dir+filename[:-3]+".tif")
            data=None
            qualcheerrore=qualcheerrore+1
            if os.path.isfile(temp_dir+filename[:-3]+'.tif') == True: os.remove(temp_dir+filename[:-3]+'.tif')
            if os.path.isfile(temp_dir+filename[:-3]+'.xml') == True: os.remove(temp_dir+filename[:-3]+'.xml')
            continue
        if (np.max(arr)<0):
            data=None
            logging.debug("[CMEMS_PROCESSORS] No valid pixel in "+filename+". No product generated")
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True: os.remove(temp_dir+filename[:-3]+".xml")
            continue
        
        ######################
        ##SST  processing
        #

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
            logging.debug("[CMEMS_PROCESSORS] Error in writing geophyisical file "+prod_filename_num)
            qualcheerrore=qualcheerrore+1
        else:
            #Apply the legend to the newly created file
            loggio=[]
            lalegenda=Read_Legend(Legends[iin],loggio)
            for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
            if lalegenda[0] != 0 or lalegenda[1] != 0:
                loggio=[]
                Re,Ge,Be=Apply_Legend(output_dir+prod_filename_num,-1,lalegenda,loggio)
                for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
                lalegenda=None
                if (len(Re[0]) > 1):
                    loggio=[]
                    res=RGB_as_input(output_dir+prod_filename_num,Re,Ge,Be,output_dir+prod_filename_the,loggio)
                    for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
                    Re=None
                    Ge=None
                    Be=None
                    if res == 1:
                        #ErrorMessage is already set
                        a=1
                else:
                    #ErrorMessage is already set
                    a=1
            else:
                #ErrorMessage is already set
                a=1

        data=None
        #Delete intermediate files
        os.remove(temp_dir+filename[:-3]+".tif")
        if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
            os.remove(temp_dir+filename[:-3]+".xml")
        continue
   
    if (qualcheerrore>0):
        return 1

    return 0


########
## CHL_Processing
##
## Processing of CHL dataset-oc-med-chl-multi-l3-chl_1km_daily-rt-v02
##
## inputlist: list of files to (singularly) process
## overwrite: 1 = overwrite products if already existing
## AOI: 1=Italy/Adriatic 2=Greece (any other == Italy)
## output_dir: it must contain a date and it will be compared with the one inside the input product
## 
def CHL_Chain(inputlist,overwrite,AOI, output_dir):
    
    #CHL product internal index
    iin=0

    #Checks AOI
    if (AOI!=1) and (AOI!=2):
        logging.debug("[CMEMS_PROCESSORS] Wrong AOI parameter, set to Adriatic")
        AOI=1
    AOI=AOI-1

    logging.info("[CMEMS_PROCESSORS] Selected parameter: Chlorophyll")
    #
    #GPT Processing of each single dataset (in CMEMS it will be always a single one)
    #
    qualcheerrore=0
    for n in range(0,len(inputlist)):
        filename=os.path.basename(inputlist[n])

        if (len(filename) == 0):
            logging.debug("[CMEMS_PROCESSORS] Wrong filename for Chl input "+input_dir+filename)
            qualcheerrore=qualcheerrore+1
            continue

        # Definition of final filename taking acquisition date from .nc metadata
        ncdvars = nc.netcdf_file(input_dir+filename, 'r').variables
        timekey=ncdvars.get('time')
        time=timekey.getValue()
        t0 = datetime.datetime(1981, 1, 1)
        dt = t0 + datetime.timedelta(seconds=time)
        me=str(dt.month)
        da=str(dt.day)
        if len(me)==1: me='0'+me
        if len(da)==1: da='0'+da
        verifdate=str(dt.year)+'-'+me+'-'+da
        if output_dir.find(verifdate)== -1:
            logging.debug("[CMEMS_PROCESSORS] The date into the product ("+verifdate+") differs from the one of the outputdir("+output_dir+")")
            logging.debug("[CMEMS_PROCESSORS] Product not generated !!")
            continue
        dated_filename='RC_'+AOI_Name[AOI]+'_'+str(dt.year)+me+da
        prod_filename_num=dated_filename+"_"+pFilenames[iin]+"_Num.tif"
        prod_filename_the=dated_filename+"_"+pFilenames[iin]+"_Thematic.tif"

        #Check if the corresponding output has been already generated
        if overwrite==0:
            if os.path.exists(output_dir+prod_filename_num) and os.path.exists(output_dir+prod_filename_the):
                logging.debug("[CMEMS_PROCESSORS] "+filename+" already processed !")
                continue
        
        ##############
        ##CHL  pre-processing
        #

        # Processing with SNAP
        commando=[snap,'-e',GPT_Chl_Graph[AOI],'-Pfilein='+input_dir+filename,
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
            logging.debug("[CMEMS_PROCESSORS] Error in pre-processing "+filename)
            qualcheerrore=qualcheerrore+1
            continue
       
        #Check if there is at least a valid pixels, otherwise delete it
        try:
            data=gdal.Open(temp_dir+filename[:-3]+".tif")
            band=data.GetRasterBand(1)
            arr=band.ReadAsArray()
        except RuntimeError:
            logging.debug("[CMEMS_PROCESSORS] Error in reading file "+temp_dir+filename[:-3]+".tif")
            data=None
            qualcheerrore=qualcheerrore+1
            if os.path.isfile(temp_dir+filename[:-3]+'.tif') == True: os.remove(temp_dir+filename[:-3]+'.tif')
            if os.path.isfile(temp_dir+filename[:-3]+'.xml') == True: os.remove(temp_dir+filename[:-3]+'.xml')
            continue
        if (np.max(arr)<0):
            data=None
            logging.debug("[CMEMS_PROCESSORS] No valid pixel in "+filename+". No product generated")
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True: os.remove(temp_dir+filename[:-3]+".xml")
            continue
        
        ######################
        ##CHL  processing
        #

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
            logging.debug("[CMEMS_PROCESSORS] Error in writing geophyisical file "+prod_filename_num)
            qualcheerrore=qualcheerrore+1
        else:
            #Apply the legend to the newly created file
            loggio=[]
            lalegenda=Read_Legend(Legends[iin],loggio)
            for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
            if lalegenda[0] != 0 or lalegenda[1] != 0:
                loggio=[]
                Re,Ge,Be=Apply_Legend(output_dir+prod_filename_num,-1,lalegenda,loggio)
                for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
                lalegenda=None
                if (len(Re[0]) > 1):
                    loggio=[]
                    res=RGB_as_input(output_dir+prod_filename_num,Re,Ge,Be,output_dir+prod_filename_the,loggio)
                    for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
                    Re=None
                    Ge=None
                    Be=None
                    if res == 1:
                        #Error message already logged
                        a=1
                else:
                    #Error message already logged
                    a=1
            else:
                #Error message already logged
                a=1

        data=None
        #Delete intermediate files
        os.remove(temp_dir+filename[:-3]+".tif")
        if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
            os.remove(temp_dir+filename[:-3]+".xml")
        continue      
    
    if (qualcheerrore>0):
        return 1

    return 0


########
## TWT_Processing
##
## Processing of Tubidity or Water Transparency
## Set of datasets required in the right order
##
## inputlist: list of files to (singularly) process
## overwrite: 1 = overwrite products if already existing
## qual: 1==Turbidity
##       2==Water Transparency
## AOI: 1=Italy/Adriatic 2=Greece (any other == Italy)
## output_dir: it must contain a date and it will be compared with the one inside the input product
##
## 
def TWT_Chain(inputlist,overwrite,qual,AOI, output_dir):
    

    #product internal index
    if qual == 1:
        iin=2
    elif qual == 2:
        iin=1
    else:
        logging.debug("[CMEMS_PROCESSORS] No WT or Turbidity produt requested")
        return 1

    #Checks AOI
    if (AOI!=1) and (AOI!=2):
        logging.debug("[CMEMS_PROCESSORS] Wrong AOI parameter, set to Adriatic")
        AOI=1
    AOI=AOI-1

    if qual==1:
        logging.info("[CMEMS_PROCESSORS] Selected parameter: Turbidity")
    else:
        logging.info("[CMEMS_PROCESSORS] Selected parameter: Water Transparency")
        
    #
    #GPT Processing of each single data (in CMEMS it will be always a single one)
    #
    qualcheerrore=0
    for n in range(0,len(inputlist)):

        for filename in inputlist[n]:
            if (len(filename) == 0):
                logging.debug("[CMEMS_PROCESSORS] Wrong filename for WT/Tur input "+input_dir+filename)
                qualcheerrore=qualcheerrore+1
                continue

        filename=os.path.basename(inputlist[n][0])

        # Definition of final filename taking acquisition date from .nc metadata
        ncdvars = nc.netcdf_file(input_dir+filename, 'r').variables
        timekey=ncdvars.get('time')
        time=timekey.getValue()
        t0 = datetime.datetime(1981, 1, 1)
        dt = t0 + datetime.timedelta(seconds=time)
        me=str(dt.month)
        da=str(dt.day)
        if len(me)==1: me='0'+me
        if len(da)==1: da='0'+da
        verifdate=str(dt.year)+'-'+me+'-'+da
        if output_dir.find(verifdate)== -1:
            logging.debug("[CMEMS_PROCESSORS] The date into the product ("+verifdate+") differs from the one of the outputdir("+output_dir+")")
            logging.debug("[CMEMS_PROCESSORS] Product not generated !!")
            continue
        dated_filename='RC_'+AOI_Name[AOI]+'_'+str(dt.year)+me+da
        prod_filename_num=dated_filename+"_"+pFilenames[iin]+"_Num.tif"
        prod_filename_the=dated_filename+"_"+pFilenames[iin]+"_Thematic.tif"

        #Check if the corresponding output has been already generated
        if overwrite==0:
            if os.path.exists(output_dir+prod_filename_num) and os.path.exists(output_dir+prod_filename_the):
                logging.debug("[CMEMS_PROCESSORS] "+filename+" already processed !")
                continue
        
        ##############
        ##WT_Tur  pre-processing
        #
        filepreout_wt=temp_dir+filename[:-3]+'_tur.tif'
        filepreout_tur=temp_dir+filename[:-3]+'_wt.tif'
        if qual==1: #Turbidity
            filepreout_wt=temp_dir+'dummy.tif'            
        else: #Water Transparency
            filepreout_tur=temp_dir+'dummy.tif'

        # Processing with SNAP
        commando=[snap,'-e',GPT_TWT_Graph[AOI],
                  '-Pfilein490='+inputlist[n][0],
                  '-Pfilein555='+inputlist[n][1],
                  '-Pfilein670='+inputlist[n][2],
                  '-PfileinKd='+inputlist[n][3],
                  '-Pmaskin='+Mask_LandSea[AOI],
                  '-PfileoutWT='+filepreout_wt,
                  '-PfileoutTur='+filepreout_tur,
                  '-Pformat=GeoTIFF+XML']
        
        try:
            erro=0
            subprocess.check_call(commando)
        except subprocess.CalledProcessError:
            erro=1

        if (erro==1) or os.path.exists(filepreout_wt)==None or os.path.exists(filepreout_tur)==None:
            if os.path.isfile(filepreout_wt) == True: os.remove(filepreout_wt)
            if os.path.isfile(filepreout_wt[:-4]+".xml") == True: os.remove(filepreout_wt[:-4]+".xml")
            if os.path.isfile(filepreout_tur) == True: os.remove(filepreout_tur)
            if os.path.isfile(filepreout_tur[:-4]+".xml") == True: os.remove(filepreout_tur[:-4]+".xml")
            #If GPT fails report it, but continues to next file
            logging.debug("[CMEMS_PROCESSORS] Error in pre-processing "+filename)
            qualcheerrore=qualcheerrore+1
            continue

        if os.path.exists(temp_dir+'dummy.tif'): os.remove(temp_dir+'dummy.tif')
        if os.path.exists(temp_dir+'dummy.xml'): os.remove(temp_dir+'dummy.xml')
        
        if qual==1: #Turbidity
            filepreout=filepreout_tur
        else: #Water Transparency
            filepreout=filepreout_wt
       
        #Check if there is at least a valid pixels, otherwise delete it
        try:
            data=gdal.Open(filepreout)
            band=data.GetRasterBand(1)
            arr=band.ReadAsArray()
        except RuntimeError:
            logging.debug("[CMEMS_PROCESSORS] Error in reading file "+filepreout)
            data=None
            qualcheerrore=qualcheerrore+1
            if os.path.isfile(filepreout) == True: os.remove(filepreout)
            if os.path.isfile(filepreout[:-4]+".xml") == True: s.remove(filepreout[:-4]+".xml")
            continue

        if (np.max(arr)<0):
            data=None
            logging.debug("[CMEMS_PROCESSORS] No valid pixel in "+filepreout+". No product generated")
            os.remove(filepreout)
            if os.path.isfile(filepreout[:-4]+".xml") == True: os.remove(filepreout[:-4]+".xml")
            continue

        ######################
        ##WT_Tur  processing
        #

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
            logging.debug("[CMEMS_PROCESSORS] Error in writing geophyisical file "+prod_filename_num)
            qualcheerrore=qualcheerrore+1
        else:
            #Apply the legend to the newly created file
            loggio=[]
            lalegenda=Read_Legend(Legends[iin],loggio)
            for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
            if lalegenda[0] != 0 or lalegenda[1] != 0:
                loggio=[]
                Re,Ge,Be=Apply_Legend(output_dir+prod_filename_num,-1,lalegenda,loggio)
                for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
                lalegenda=None
                if (len(Re[0]) > 1):
                    loggio=[]
                    res=RGB_as_input(output_dir+prod_filename_num,Re,Ge,Be,output_dir+prod_filename_the,loggio)
                    for lili in loggio: logging.debug("[CMEMS_PROCESSORS] "+lili)
                    Re=None
                    Ge=None
                    Be=None
                    if res == 1:
                        #ErrorMessage is already set
                        a=1
                else:
                    #ErrorMessage is already set
                    a=1
            else:
                #ErrorMessage is already set
                a=1

        data=None
        #Delete intermediate files
        os.remove(filepreout)
        if os.path.isfile(filepreout[:-4]+".xml") == True: os.remove(filepreout[:-4]+".xml")
        continue      
    
    if (qualcheerrore>0):
        return 1

    return 0

############ --------MAIN PROCEDURE ------------------
##########
## WQ_CMEMS_Chain
##
## Input:
##   onflag: bit 0 -> sst
##           bit 1 -> chl
##           bit 2 -> wt
##           bit 3 -> tur
##   ovewflag: same bit order of onflag. When set to 1, it activates overwriting of already existing products
##   date: date to be processed, which will be the output folder subdir
##   setAOI: 1=ITA, 2=GRE, Any other=BOTH
##   
##
## Output: 0 okay, 1 any error
##
def WQ_CMEMS_Chain(
        onflag,
        ovrwflag,
        date,
        setAOI=[1,2]):

    # Not useful when setAOI is set and not passed as argument
	#if setAOI!=1 and setAOI!=2:
    #    setAOI=[1,2]
    #else:
    #    setAOI=[setAOI]
    #global output_dir

    
    dest_dir = "%s/" %os.path.join(global_output_dir, date)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    for areaofi in setAOI:
        logging.info("[CMEMS_PROCESSORS] Processing AOI: "+AOI_Name[areaofi-1])
        
        eerr=0
        ###SST section
        if (onflag & 1)!=0:
            ovrw=0
            if (ovrwflag & 1)!=0: ovrw=1    
            #Search for SST input files
            ce=glob.glob(input_dir+SST_input_f+'*'+date+'.nc')
            if len(ce)==0:
                logging.debug("[CMEMS_PROCESSORS] "+'No SST input files to process with specified date: '+date)
            else:
                result1=SST_Chain(ce,ovrw,areaofi, dest_dir)
                if result1==1: eerr=1

        ###CHL section
        if (onflag & 2)!=0:
            ovrw=0
            if (ovrwflag & 2)!=0: ovrw=1
            #Search for CHL input files
            ce=glob.glob(input_dir+CHL_input_f+'*'+date+'.nc')
            if len(ce)==0:
                logging.debug("[CMEMS_PROCESSORS] "+'No CHL input files to process with specified date: '+date)
            else:
                result2=CHL_Chain(ce,ovrw,areaofi, dest_dir)
                if result2==1: eerr=1
       
        ###WT&Tur common section
        if (onflag & 4)!=0 or (onflag & 8)!=0:
            #Searches the input files for one or both
            glifile=[]
            badlist=0
            #Search for WT/TUR input files
            for en in range(len(OC_input_f)):
                tipi=OC_input_f[en]
                ce=glob.glob(input_dir+tipi+'*'+date+'.nc')
                if len(ce)==0:
                     logging.debug("[CMEMS_PROCESSORS] No >"+tipi+"< input files to process with specified date: "+date)
                     badlist=1
                     break
                glifile.append(ce)
            
            if badlist==0:
                #Chech what found for set of n files
                for en in range(1,len(OC_input_f)):
                    if len(glifile[en]) != len(glifile[en-1]):
                        logging.debug("[CMEMS_PROCESSORS] Missing set of input files to process for WT/Tur ("+OC_input_f[en]+")")
                        badlist=1
                        break

            #Sort what found into a single list of lists
            findtable=[]
            if badlist==0:
                for en in range(len(glifile[0])):
                    lst=[]
                    for ne in range(len(OC_input_f)):
                        lst.append(glifile[ne][en])
                    findtable.append(lst)            

        ###WT specific
        if (onflag & 4)!=0:
            ovrw=0
            if (ovrwflag & 4)!=0: ovrw=1
            if len(findtable)!=0:
                result3=TWT_Chain(findtable,ovrw,2,areaofi, dest_dir)
                if result3==1: eerr=1
                

        #Tur specific
        if (onflag & 8)!=0:
            ovrw=0
            if (ovrwflag & 8)!=0: ovrw=1
            if len(findtable)!=0:
                result4=TWT_Chain(findtable,ovrw,1,areaofi, dest_dir)
                if result4==1: eerr=1
            
    if eerr==1:
        return 1,dest_dir

    return 0,dest_dir

if __name__ == '__main__':

##Manual testing
    logging.info("Main body.")

    res=WQ_CMEMS_Chain(15,0,'2017-05-30')
    print res

    logging.info("Ended.")						  
