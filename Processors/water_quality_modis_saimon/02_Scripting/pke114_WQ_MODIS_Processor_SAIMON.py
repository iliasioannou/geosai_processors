#
# Version of 04/05/2016
#
# Open issues:
# - only used AQUA data [design choice]
#
import os
import sys
import ntpath
import subprocess
import urllib2
import time
import gdal
from glob import iglob
import numpy as np
import datetime

from pke114_Apply_Legend import Read_Legend ##Need to be in the same folder
from pke114_Apply_Legend import Apply_Legend ##Need to be in the same folder
from pke114_Apply_Legend import RGB_as_input ##Need to be in the same folder


############
## Pre-fixed information
##
#General
input_dir=""



###---------------------------------------------------------------------------
###SET UP LOCAL ON MASERATI
temp_dir="D:/pke114_WQ_SAIMON/04_TempDir/"
output_dir="D:/pke114_WQ_SAIMON/05_OutputDir/"
## Other settings which need to be defined somewhere
if 'snap' not in globals():
    snap="C:/Programmis/snap/bin/gpt"
if 'ErrorMessage' not in globals():
    ErrorMessage=[]
    
###SAIMON related 
GPT_WQ_Graph="D:/pke114_WQ_SAIMON/02_Scripting/WQ_Graph_SAI.xml"
GPT_SST_Graph="D:/pke114_WQ_SAIMON/02_Scripting/SST_Graph_SAI.xml"
GPT_WQ_M_Graph="D:/pke114_WQ_SAIMON/02_Scripting/Mosaic_WQ_Graph.xml"
GPT_SST_M_Graph="D:/pke114_WQ_SAIMON/02_Scripting/Mosaic_SST_Graph.xml"
pFilenames=['Chl','WT','Tur','SST']
Legends=['D:/pke114_WQ_SAIMON/01_Ancillari/Legenda_CHL.txt',
         'D:/pke114_WQ_SAIMON/01_Ancillari/Legenda_TR.txt',
         'D:/pke114_WQ_SAIMON/01_Ancillari/Legenda_Turb_provv.txt',
         'D:/pke114_WQ_SAIMON/01_Ancillari/Legenda_SST.txt']
Mask_LandSea="D:/pke114_WQ_SAIMON/01_Ancillari/Mask_Sea_thesprotia_AOI.tif"
###---------------------------------------------------------------------------

def run(argsDict):
        
    #raise Exception('SIMULATED EXCEPTION!')
    #return { "returnCode": 0,  "outPath": shared_path }
    return { "returnCode": WQ_Chain(argsDict),  "outPath": shared_path }

#########################################################################
### procedures
##############
## parse_input
## Parses input
## Return dates and links or 0,''
def parse_input(argsDict):
    if(argsDict):
       p_count = int(argsDict["count"])
       pA_links = [ argsDict["OC"], argsDict["SST"] ]
    else:
        return 0,''
    
    print "Parsed count:", p_count
    print "Parsed links:", pA_links
    
    return p_count,pA_links

##
# get_shape_boundaries
# Gets the (largest) boudaries of the input shapefile
# Returns: minlon,maxlon,minlat,maxlat
##
def get_shape_boundaries(shapename):
    "Gets the (largest) boudaries of the input shapefile. Returns: minlon,maxlon,minlat,maxlat"
    
    driver=ogr.GetDriverByName("ESRI Shapefile")
    shp=driver.Open(shapename,0)
    layer = shp.GetLayer()
    feature = layer.GetNextFeature()

    minlon=180
    maxlon=0
    minlat=90
    maxlat=-90

    while feature:
        env=feature.GetGeometryRef().GetEnvelope()
        minlon=min(env[0],minlon)
        minlat=min(env[2],minlat)
        maxlon=max(env[1],maxlon)
        maxlat=max(env[3],maxlat)
        feature = layer.GetNextFeature()

    shp.Destroy()
    shp=None
    layer=None

    return [minlon,maxlon,minlat,maxlat]

################
## get_http
## Download a file from <url> to the folder <destdir>
## Returns:
## 1) the name of the file if successfull otherwise a void string
## 2) the description of the error if unsuccessfull otherwise a void string
##
def get_http(url,destdir):
    attempts=4
    for repeat in range(attempts+1):
        try:
            file_name = url.split('/')[-1]
            print "Download ",file_name
            u = urllib2.urlopen(url)
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            #Checks if already downloaded
            #Mainly for fasten debug
            if os.path.isfile(destdir+file_name)==True:
                if (os.path.getsize(destdir+file_name) == file_size ):
                    return file_name,''
            f = open(destdir+file_name, 'wb')
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                f.write(buffer)
            f.close()
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                errore='Failed to reach a server. Reason: '+str(e.reason)
            elif hasattr(e, 'code'):
                errore="The server couldn\'t fulfill the request. Error code: "+str(e.code)
        except IOError as e:
            errore="I/O error("+"{0}): {1}".format(e.errno, e.strerror)
        except:
            errore="Unexpected error:", sys.exc_info()
        else:
            if (os.path.getsize(destdir+file_name) == file_size ):
                return file_name,''

        #Waits 3 minutes and retries
        print "Wait to retry"
        time.sleep(180)

    return '',errore

##
## Launches Intelligent Merging by using SNAP
## Input files should be GeoTIFF generated with SNAP, sinc they need to
## have a tag with the band names
## OC=1 for WQ and OC=0 for SST
##
## The output file name will have a mean value within the
## timing of the two scenes
##
def scene_merging(file_1,file_2,OC,outdir):
    if (OC==1):
        grapho=GPT_WQ_M_Graph
    else:
        grapho=GPT_SST_M_Graph

    finame=os.path.basename(file_1)
    time1=int(finame[8:14])
    finame=os.path.basename(file_2)
    time2=int(finame[8:14])
    timem=int((time1+time2)/2)
    timem=str(timem)
    if len(timem)<6:
        timem='0'+timem
    #Check for the result of the mean
    if int(timem[2:4])>59:
        timem=timem[0:2]+'55'+timem[4:6]
    if int(timem[4:6])>59:
        timem=timem[:-2]+'50'
    timem=timem[:-1]+'5'    #Add this final 5 to make clear (if needed) that it is a merging output
    finalname=finame[0:8]+timem+finame[14:]

    # Merging with SNAP
    commando=snap+" -e "+grapho+" -Pfilein1="+file_1
    commando=commando+" -Pfilein2="+file_2
    commando=commando+" -Pfileout="+outdir+finalname
    commando=commando+" -Pformat=GeoTIFF+XML"

    try:
        subprocess.check_call(commando)
    except subprocess.CalledProcessError as e:
        #If GPT fails report it, but continues to next file
        ErrorMessage.append("Error in processing "+finalname+"("+str(e.returncode)+")")
        a=subprocess.CalledProcessError
        qualcheerrore=qualcheerrore+1
        return ''

    return finalname
    

##
## WQ_Processing
##
## Deve poter accedere a tutte le variabili globali definite all'inizio
def WQ_Chain(argsDict):
    global ErrorMessage

    count,A_links=parse_input(argsDict)
    if count==0:
        ErrorMessage.append("Error parsing input information")
        return 1

    if os.path.isfile(snap+'.exe') == False:
        ErrorMessage.append("SNAP executable not found")
        return 1    
        
    #
    #GPT Processing of each single data
    #
    qualcheerrore=0
    for n in range(0,count):
        
        ##OC files processing
        #
        # Download
        theurl=A_links[0][n]
        ###print theurl

        filename,err=get_http(theurl,temp_dir)
        if (len(filename) == 0):
            #If download fails report it, but continues to next file
            ErrorMessage.append("Error in downloading "+theurl)
            ErrorMessage.append(err)
            qualcheerrore=qualcheerrore+1
            continue

        # Processing with SNAP    
        commando=snap+" -e "+GPT_WQ_Graph+" -Pfilein="+temp_dir+filename
        commando=commando+" -Pmaskin="+Mask_LandSea
        commando=commando+" -Pfileout="+temp_dir+filename[:-3]+".tif"
        commando=commando+" -Pformat=GeoTIFF+XML"

        try:
            subprocess.check_call(commando)
        except subprocess.CalledProcessError as e:
            #If GPT fails report it, but continues to next file
            ErrorMessage.append("Error in processing "+filename+"("+str(e.returncode)+")")
            a=subprocess.CalledProcessError
            qualcheerrore=qualcheerrore+1
            continue

        #Check if there is at least a valid pixels, otherwise delete it
        try:
            data=gdal.Open(temp_dir+filename[:-3]+".tif")
            band=data.GetRasterBand(1)
            arr=band.ReadAsArray()
            data=None
        except RuntimeError, e:
            ErrorMessage.append("Error in reading file "+filename)
            ErrorMessage.append(e)
            qualcheerrore=qualcheerrore+1
            continue
        if (np.max(arr)<0):
            print "Cancello! ",temp_dir+filename[:-3]+".tif"
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
                os.remove(temp_dir+filename[:-3]+".xml")

        ##SST files processing
        #
        # Download
        theurl=A_links[1][n]
        ###print theurl

        filename,err=get_http(theurl,temp_dir)
        if (len(filename) == 0):
            #If download fails report it, but continues to next file
            ErrorMessage.append("Error in downloading "+theurl)
            ErrorMessage.append(err)
            qualcheerrore=qualcheerrore+1
            continue

        # Processing with SNAP
        commando=snap+" -e "+GPT_SST_Graph+" -Pfilein="+temp_dir+filename
        commando=commando+" -Pmaskin="+Mask_LandSea
        commando=commando+" -Pfileout="+temp_dir+filename[:-3]+".tif"
        commando=commando+" -Pformat=GeoTIFF+XML"
        try:
            subprocess.check_call(commando)
        except subprocess.CalledProcessError as e:
            #If GPT fails report it, but continues to next file
            ErrorMessage.append("Error in processing "+filename+"("+str(e.returncode)+")")
            a=subprocess.CalledProcessError
            qualcheerrore=qualcheerrore+1
            continue
        
        #Check if there is at least a valid pixels, otherwise delete it
        try:
            data=gdal.Open(temp_dir+filename[:-3]+".tif")
            band=data.GetRasterBand(1)
            arr=band.ReadAsArray()
            data=None
        except RuntimeError, e:
            ErrorMessage.append("Error in reading file "+filename)
            ErrorMessage.append(e)
            qualcheerrore=qualcheerrore+1
            continue
        if (np.max(arr)<0):
            print "Cancello! ",temp_dir+filename[:-3]+".tif"
            os.remove(temp_dir+filename[:-3]+".tif")
            if os.path.isfile(temp_dir+filename[:-3]+".xml") == True:
                os.remove(temp_dir+filename[:-3]+".xml")

    ######################
    ##OC files processing
    #
    #Groups OC outputs per date to check if any with >1 scene per date
    #
    dateslist=['']
    fileslist=[['']]
    for fname in iglob(temp_dir+'A*LAC_OC.tif'):
        fname=os.path.basename(fname)
        ladate=fname[0:8]
        lst=int(fname[13])
        if (lst == 5):
            continue
        if ladate in dateslist:
            indic=dateslist.index(ladate)
            fileslist[indic].append(fname)
        else:
            dateslist.append(ladate)
            fileslist.append([fname])
    if (len(dateslist)==1):
        ErrorMessage.append("No dates processed so far")
    else:
        #Processes all the days
        for d in range(1,len(dateslist)):
            scenes=fileslist[d]
            ###print "Scena ",d," fili:",scenes
            #For each date, if more than 1 scene is present, then merges them into a new scene
            #assigning an intermediate timing
            if len(scenes) >1:
                mergefile=scene_merging(temp_dir+scenes[0],temp_dir+scenes[1],1,temp_dir)
                if len(scenes) >2:
                    mergefile=scene_merging(temp_dir+mergefile,temp_dir+scenes[2],1,temp_dir)
                #If more than 3 scenes (!!!!) ignore it.
                filename=mergefile            
            else:
                filename=scenes[0]

            #Reads the generated product
            try:
                data=gdal.Open(temp_dir+filename)
                band=data.GetRasterBand(1)
                arr=band.ReadAsArray()
            except RuntimeError, e:
                ErrorMessage.append("Error in reading file "+filename)
                ErrorMessage.append(e)
                qualcheerrore=qualcheerrore+1
                continue
        
            [cols,rows] = arr.shape
            trans       = data.GetGeoTransform()
            proj        = data.GetProjection()
            arr=None
            band=None

            # Final filename translating julian to normal date
            anno=filename[1:5]
            jul=filename[5:8]
            norm_date=datetime.datetime(int(anno),1,1)+datetime.timedelta(int(jul)-1)
            norm_month='0'+str(norm_date.month)
            norm_day='0'+str(norm_date.day)
            dated_filename=filename[0]+str(norm_date.year)+norm_month+norm_day[-2:]
            # Create a single file for each product
            for i in range(3):
                if (pFilenames[i] == 'Tur'):   #!!!!!!!!!!!!!!!!
                    continue                   #!!!!!!!!!!!!!!!!
                try:
                    outdriver = gdal.GetDriverByName("GTiff")
                    outdata   = outdriver.Create(output_dir+dated_filename+"_"+pFilenames[i]+"_Num.tif", rows, cols, 1, gdal.GDT_Float32)

                    band=data.GetRasterBand(i+1)
                    arr=band.ReadAsArray()
                    
                    outdata.GetRasterBand(1).WriteArray(arr)
                    outdata.SetGeoTransform(trans)
                    outdata.SetProjection(proj)
                    outdata=None
                    arr=None
                    band=None
                except RuntimeError, e:
                    #If not generated, still continue
                    ErrorMessage.append("Error in writing geophyisical file "+pFilenames[i]+"_Num.tif")
                    ErrorMessage.append(e)
                    qualcheerrore=qualcheerrore+1
                else:
                    #Apply the legend to the newly created file
                    lalegenda=Read_Legend(Legends[i])
                    if lalegenda[0] != 0 or lalegenda[1] != 0:
                        Re,Ge,Be=Apply_Legend(output_dir+dated_filename+"_"+pFilenames[i]+"_Num.tif",-1,lalegenda)
                        lalegenda=None
                        if (len(Re[0]) > 1):
                            res=RGB_as_input(output_dir+dated_filename+"_"+pFilenames[i]+"_Num.tif",Re,Ge,Be,output_dir+dated_filename+"_"+pFilenames[i]+"_Thematic.tif")
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

    ######################
    ##SST files processing
    #
    #Groups SST outputs per date to check if any with >1 scene per date
    #
    dateslist=['']
    fileslist=[['']]
    for fname in iglob(temp_dir+'A*LAC_SST.tif'):
        fname=os.path.basename(fname)
        ladate=fname[0:8]
        lst=int(fname[13])
        if (lst == 5):
            continue
        if ladate in dateslist:
            indic=dateslist.index(ladate)
            fileslist[indic].append(fname)
        else:
            dateslist.append(ladate)
            fileslist.append([fname])

    if (len(dateslist)==1):
        ErrorMessage.append("No dates processed so far")
    else:
        for d in range(1,len(dateslist)):
            scenes=fileslist[d]
            ###print "Scena ",d," fili:",scenes
            #For each date, if more than 1 scene is present, then merges them into a new scene
            #assigning an intermediate timing
            if len(scenes) >1:
                mergefile=scene_merging(temp_dir+scenes[0],temp_dir+scenes[1],0,temp_dir)
                if len(mergefile)==0:
                    ErrorMessage.append("Error in merging files "+scenes[0]+" and "+scenes[1])
                    qualcheerrore=qualcheerrore+1
                    continue
                if len(scenes)>2:
                    new_mergefile=scene_merging(temp_dir+mergefile,temp_dir+scenes[2],0,temp_dir)
                    if len(new_mergefile)==0:
                        ErrorMessage.append("Error in merging files "+scenes[0]+" and "+scenes[1])
                        qualcheerrore=qualcheerrore+1
                    else:
                        mergefile=new_mergefile
                #If more than 3 scenes (!!!!) ignore it.
                filename=mergefile            
            else:
                filename=scenes[0]

            #Reads the generated product
            try:
                data=gdal.Open(temp_dir+filename)
                band=data.GetRasterBand(1)
                arr=band.ReadAsArray()
            except RuntimeError, e:
                ErrorMessage.append("Error in reading file "+filename)
                ErrorMessage.append(e)
                qualcheerrore=qualcheerrore+1
                continue
        
            [cols,rows] = arr.shape
            trans       = data.GetGeoTransform()
            proj        = data.GetProjection()
            arr=None
            band=None

            # Final filename translating julian to normal date
            anno=filename[1:5]
            jul=filename[5:8]
            norm_date=datetime.datetime(int(anno),1,1)+datetime.timedelta(int(jul)-1)
            norm_month='0'+str(norm_date.month)
            norm_day='0'+str(norm_date.day)
            dated_filename=filename[0]+str(norm_date.year)+norm_month+norm_day[-2:]
            # Create the output files
            i=3
            try:
                outdriver = gdal.GetDriverByName("GTiff")
                outdata   = outdriver.Create(output_dir+dated_filename+"_"+pFilenames[i]+"_Num.tif", rows, cols, 1, gdal.GDT_Float32)

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
                ErrorMessage.append("Error in writing geophyisical file "+pFilenames[i]+"_Num.tif")
                ErrorMessage.append(e)
                qualcheerrore=qualcheerrore+1
            else:
                #Apply the legend to the newly created file
                lalegenda=Read_Legend(Legends[i])
                if lalegenda[0] != 0 or lalegenda[1] != 0:
                    Re,Ge,Be=Apply_Legend(output_dir+dated_filename+"_"+pFilenames[i]+"_Num.tif",-1,lalegenda)
                    lalegenda=None
                    if (len(Re[0]) > 1):
                        res=RGB_as_input(output_dir+dated_filename+"_"+pFilenames[i]+"_Num.tif",Re,Ge,Be,output_dir+dated_filename+"_"+pFilenames[i]+"_Thematic.tif")
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
    
    if (qualcheerrore>0):
        return 2

    if (len(ErrorMessage) > 0):
        print ErrorMessage
    return 0

	
if __name__ == '__main__':

    print "Main body."
    
    #  If input file already downloaded, odd behaviour (print filename 5 times for all files than crash)
    
    #  File "processor-test.py", line 537, in <module>
    #    resulto=WQ_Chain(testDict)
    #  File "processor-test.py", line 458, in WQ_Chain
    #    mergefile=scene_merging(temp_dir+mergefile,temp_dir+scenes[2],0,temp_dir)
    #   TypeError: cannot concatenate 'str' and 'NoneType' objects
    #
    testDict = {"count":4, "OC":['http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2016121110000.L2_LAC_OC.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2016121124000.L2_LAC_OC.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2016114105500.L2_LAC_OC.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2016114123000.L2_LAC_OC.nc'], "SST":['http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2016121110000.L2_LAC_SST.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2016121124000.L2_LAC_SST.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2016114105500.L2_LAC_SST.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2016114123000.L2_LAC_SST.nc']}
    
    #testDict = {"count":3, "OC":['http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2015241122000.L2_LAC_OC.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2015242112500.L2_LAC_OC.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2015243120500.L2_LAC_OC.nc'], "SST":['http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2015241122000.L2_LAC_SST.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2015242112500.L2_LAC_SST.nc', 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A2015243120500.L2_LAC_SST.nc']}
    
    resulto=WQ_Chain(testDict)
    
    if resulto == 0:
        print "All ok."
    else:
        print ErrorMessage




