#
# Version of 29/05/2017
#
# TO DO:
#       - include Turbidity and Water Transparency
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
ancil_dir=main_dir+"01_Ancillari/"
script_dir=main_dir+"02_Scripting/"
input_dir=main_dir+"03_Input/"
temp_dir=main_dir+"04_TempDir/"
output_dir=main_dir+"05_OutputDir/"

###CMEMS related 
SST_input_f='SST_MED_SST_L3S_NRT_OBSERVATIONS_010_012_b_'
CHL_input_f='dataset-oc-med-chl-multi-l3-chl_1km_daily-rt'
OC_input_f=['dataset-oc-med-opt-multi-l3-kd490_1km_daily-rt',
          'dataset-oc-med-opt-multi-l3-rrs490_1km_daily-rt',
          'dataset-oc-med-opt-multi-l3-rrs555_1km_daily-rt',
          'dataset-oc-med-opt-multi-l3-rrs670_1km_daily-rt']
GPT_Chl_Graph=script_dir+"Chl_Graph_CMEMS.xml"
GPT_SST_Graph=script_dir+"SST_Graph_CMEMS.xml"
GPT_WQ_M_Graph=script_dir+"Mosaic_WQ_Graph.xml"
GPT_SST_M_Graph=script_dir+"Mosaic_SST_Graph.xml"
pFilenames=['Chl','WT','Tur','SST']
Legends=[ancil_dir+'Legenda_CHL.txt',
         ancil_dir+'Legenda_TR.txt',
         ancil_dir+'Legenda_Turb.txt',
         ancil_dir+'Legenda_SST.txt']
Mask_LandSea=ancil_dir+"Mask_Sea-Land_SRTM_Adriatic.tif"

###Others
ErrorMessage=[]  
GDAL_TIFF_Options_list=['COMPRESS=LZW','TILED=YES']

###---------------------------------------------------------------------------

   

########
## SST_Processing
##
## Processing of SST CMEMS SST_MED_SST_L3S_NRT_OBSERVATIONS_010_012_b
##
## 
def SST_Chain(inputlist,overwrite):
    global ErrorMessage
    #SST product internal index
    iin=3
    #
    #GPT Processing of each single data
    #
    qualcheerrore=0
    for n in range(0,len(inputlist)):
        filename=os.path.basename(inputlist[n])

        if (len(filename) == 0):
            ErrorMessage.append("Wrong filename for SST input "+input_dir+filename)
            qualcheerrore=qualcheerrore+1
            continue

        # Definition of final filename taking acquisition date from .nc metadata
        time = nc.netcdf_file(input_dir+filename, 'r').time_min
        t0 = datetime.datetime(1981, 1, 1)
        dt = t0 + datetime.timedelta(seconds=time)
        dated_filename='RC_'+str(dt.year)+'_'+str(dt.month)+'_'+str(dt.day)
        prod_filename_num=dated_filename+"_"+pFilenames[iin]+"_Num.tif"
        prod_filename_the=dated_filename+"_"+pFilenames[iin]+"_Thematic.tif"

        #Check if the corresponding output has been already generated
        if overwrite==0:
            if os.path.exists(output_dir+prod_filename_num) and os.path.exists(output_dir+prod_filename_the):
                ErrorMessage.append(filename+" already processed !")
                continue
        

        ##############
        ##SST  pre-processing
        #

        # Processing with SNAP
        commando=[snap,'-e',GPT_SST_Graph,'-Pfilein='+input_dir+filename,
                       '-Pmaskin='+Mask_LandSea,
                       '-Pfileout='+temp_dir+filename[:-3]+'.tif',
                       '-Pformat=GeoTIFF+XML']
        
        try:
            subprocess.check_call(commando)
            a=1
        except subprocess.CalledProcessError as e:
            #If GPT fails report it, but continues to next file
            ErrorMessage.append("Error in pre-processing "+filename)
            qualcheerrore=qualcheerrore+1
            continue
       
        #Check if there is at least a valid pixels, otherwise delete it
        try:
            data=gdal.Open(temp_dir+filename[:-3]+".tif")
            band=data.GetRasterBand(1)
            arr=band.ReadAsArray()
        except RuntimeError, e:
            ErrorMessage.append("Error in reading file "+temp_dir+filename[:-3]+".tif")
            data=None
            qualcheerrore=qualcheerrore+1
            continue
        if (np.max(arr)<0):
            data=None
            print "No valid pixel in "+filename+". No product generated"
            ErrorMessage.append("No valid pixel in "+filename+". No product generated")
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
                os.remove(temp_dir+filename[:-3]+".xml")
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
            ErrorMessage.append("Error in writing geophyisical file "+prod_filename_num)
            qualcheerrore=qualcheerrore+1
        else:
            #Apply the legend to the newly created file
            loggio=[]
            lalegenda=Read_Legend(Legends[iin],loggio)
            ErrorMessage=ErrorMessage+loggio
            if lalegenda[0] != 0 or lalegenda[1] != 0:
                loggio=[]
                Re,Ge,Be=Apply_Legend(output_dir+prod_filename_num,-1,lalegenda,loggio)
                ErrorMessage=ErrorMessage+loggio
                lalegenda=None
                if (len(Re[0]) > 1):
                    loggio=[]
                    res=RGB_as_input(output_dir+prod_filename_num,Re,Ge,Be,output_dir+prod_filename_the,loggio)
                    ErrorMessage=ErrorMessage+loggio
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
## 
def CHL_Chain(inputlist,overwrite):
    global ErrorMessage
    #CHL product internal index
    iin=0
    #
    #GPT Processing of each single data
    #
    qualcheerrore=0
    for n in range(0,len(inputlist)):
        filename=os.path.basename(inputlist[n])

        if (len(filename) == 0):
            ErrorMessage.append("Wrong filename for Chl input "+input_dir+filename)
            qualcheerrore=qualcheerrore+1
            continue

        # Definition of final filename taking acquisition date from .nc metadata
        ncdvars = nc.netcdf_file(input_dir+filename, 'r').variables
        timekey=ncdvars.get('time')
        time=timekey.getValue()
        t0 = datetime.datetime(1981, 1, 1)
        dt = t0 + datetime.timedelta(seconds=time)
        dated_filename='RC_'+str(dt.year)+'_'+str(dt.month)+'_'+str(dt.day)        
        prod_filename_num=dated_filename+"_"+pFilenames[iin]+"_Num.tif"
        prod_filename_the=dated_filename+"_"+pFilenames[iin]+"_Thematic.tif"

        #Check if the corresponding output has been already generated
        if overwrite==0:
            if os.path.exists(output_dir+prod_filename_num) and os.path.exists(output_dir+prod_filename_the):
                ErrorMessage.append(filename+" already processed !")
                continue
        
        ##############
        ##CHL  pre-processing
        #

        # Processing with SNAP
        commando=[snap,'-e',GPT_Chl_Graph,'-Pfilein='+input_dir+filename,
                  '-Pmaskin='+Mask_LandSea,
                  '-Pfileout='+temp_dir+filename[:-3]+'.tif',
                  '-Pformat=GeoTIFF+XML']
        
        try:
            subprocess.check_call(commando)
            a=1
        except subprocess.CalledProcessError as e:
            #If GPT fails report it, but continues to next file
            ErrorMessage.append("Error in pre-processing "+filename)
            qualcheerrore=qualcheerrore+1
            continue
       
        #Check if there is at least a valid pixels, otherwise delete it
        try:
            data=gdal.Open(temp_dir+filename[:-3]+".tif")
            band=data.GetRasterBand(1)
            arr=band.ReadAsArray()
        except RuntimeError, e:
            ErrorMessage.append("Error in reading file "+temp_dir+filename[:-3]+".tif")
            data=None
            qualcheerrore=qualcheerrore+1
            continue
        if (np.max(arr)<0):
            data=None
            print "No valid pixel in "+filename+". No product generated"
            ErrorMessage.append("No valid pixel in "+filename+". No product generated")
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
                os.remove(temp_dir+filename[:-3]+".xml")
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
            ErrorMessage.append("Error in writing geophyisical file "+prod_filename_num)
            qualcheerrore=qualcheerrore+1
        else:
            #Apply the legend to the newly created file
            loggio=[]
            lalegenda=Read_Legend(Legends[iin],loggio)
            ErrorMessage=ErrorMessage+loggio
            if lalegenda[0] != 0 or lalegenda[1] != 0:
                loggio=[]
                Re,Ge,Be=Apply_Legend(output_dir+prod_filename_num,-1,lalegenda,loggio)
                ErrorMessage=ErrorMessage+loggio
                lalegenda=None
                if (len(Re[0]) > 1):
                    loggio=[]
                    res=RGB_as_input(output_dir+prod_filename_num,Re,Ge,Be,output_dir+prod_filename_the,loggio)
                    ErrorMessage=ErrorMessage+loggio
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


############--------MAIN PROCEDURE ------------------
##########
## WQ_CMEMS_Chain
##
## Input:
##   onflag: bit 0 -> sst
##           bit 1 -> chl
##           bit 2 -> wt
##           bit 3 -> tur
##   ovewflag: same bit order of onflag. When set to 1, it activates overwriting of already existing products
##
## Output: 0 okay, 1 any error
##
def WQ_CMEMS_Chain(onflag,ovrwflag):
    
    if os.path.isfile(snap+'.exe') == False:
        ErrorMessage.append("SNAP executable not found")
        return -1

    ##SST section
    if (onflag & 1)!=0:
        ovrw=0
        if (ovrwflag & 1)!=0: ovrw=1    
        #Search for SST input files
        ce=glob.glob(input_dir+SST_input_f+'*.nc')
        if len(ce)==0:
            ErrorMessage.append('No SST input files to process')
        else:
            result1=SST_Chain(ce,ovrw)

    ##CHL section
    if (onflag & 2)!=0:
        ovrw=0
        if (ovrwflag & 2)!=0: ovrw=1
        #Search for CHL input files
        ce=glob.glob(input_dir+CHL_input_f+'*.nc')
        if len(ce)==0:
            ErrorMessage.append('No CHL input files to process')
        else:
            result2=CHL_Chain(ce,ovrw)
    
    if result1!=0 or result2!=0:
        return 1

    return 0

if __name__ == '__main__':

    if len(sys.argv)!=4:
        print "Wrong number of arguments!"
    else:
        param1=int(sys.argv[1])
        param2=int(sys.argv[2])
        IDS=sys.argv[3]

        ErrorMessage.append("Start: "+time.ctime())
        res=WQ_CMEMS_Chain(param1,param2)
        ErrorMessage.append("End: "+time.ctime())
        
        lg=open(output_dir+IDS+'_log.txt','w')
        for linea in ErrorMessage:
            lg.write(linea+'\n')
        lg.close()

##Manual testing
##    print "Main body."
##
##    res=WQ_CMEMS_Chain(3,3)
##    print ret
