#
# Version of 19/05/2016
#
# - Doesn't check for duplicates of daily products
#
#
import os
import sys
from osgeo import ogr, osr
import gdal
from gdalconst import *
import numpy as np
import fnmatch
import datetime

from pke114_Apply_Legend import Read_Legend ##Need to be in the same folder
from pke114_Apply_Legend import Apply_Legend ##Need to be in the same folder
from pke114_Apply_Legend import RGB_as_input ##Need to be in the same folder

############
## External information/settings, which are needed 
## 
output_dir="C:/RheticusPktProcessors/WaterQuality/Modis_Saimon/06_OutputDir_Periodic/"
pProds=['Chl','WT','SST']
SLegends=['C:/RheticusPktProcessors/WaterQuality/Modis_Saimon/01_Ancillari/Legenda_CHL.txt',
         'C:/RheticusPktProcessors/WaterQuality/Modis_Saimon/01_Ancillari/Legenda_TR.txt',
         'C:/RheticusPktProcessors/WaterQuality/Modis_Saimon/01_Ancillari/Legenda_SST.txt']
SMask_LandSea="C:/RheticusPktProcessors/WaterQuality/Modis_Saimon/01_Ancillari/Mask_Sea_thesprotia_AOI.tif"
IntNoData=10000
IntNoData1=11000
NoDataVal=-11
LandVal=-10
############

prods_dir="C:/RheticusPktProcessors/WaterQuality/Modis_Saimon/05_OutputDir/"

## Other settings which need to be defined somewhere
if 'ErrorMessage' not in globals():
    ErrorMessage=[]

#####################################################################################

def run(argsDict):
    
    #raise Exception('SIMULATED EXCEPTION!')
    
    WkDate = [int(d) for d in argsDict["runDate"].split("-")]
    # procType: 0 -> Decade; 1 -> Month
    procType = int(argsDict["procType"])
    
     # Call processor
    wqmspReturnCode=WQ_Stats_SAIMON(WkDate, procType)
    print wqmspReturnCode
    print ErrorMessage
    
    # Archive output in "runDate" folder
    outDirName = argsDict["runDate"]+"_"+argsDict["procType"]+"_"+str(wqmspReturnCode)
    
    if not os.path.exists( os.path.join(output_dir, outDirName) ):
        os.makedirs( os.path.join(output_dir+outDirName) )
    else:
        for oldoutf in os.listdir( os.path.join(output_dir, outDirName) ):
            if( os.path.isfile(os.path.join(output_dir, outDirName, oldoutf)) ):
                os.remove( os.path.join(output_dir, outDirName, oldoutf) )
    for outf in os.listdir(output_dir):
        if( os.path.isfile(os.path.join(output_dir, outf)) ):
            os.rename( os.path.join(output_dir, outf), os.path.join(output_dir, outDirName, "A"+argsDict["runDate"].replace("-","")+outf[1:]) )
    
    # Force fake alert
    #return { "returnCode": 1, "outPath": shared_path+outDirName+"\\" }
    return { "returnCode": wqmspReturnCode, "outPath": shared_path+outDirName+"\\" }


##################################
# Percentile
#
# array = array of numbers for which to calculate the Percentile
# P = percentile (1-100)
# nodata = no data value
#
# If less than 4 values are available, the P90 is not calculated.
def Percentile(array,P,nodata):  
    #remove no data values, returning a flattened array  
    flatArray = array[array != nodata]
    #sorts array
    flatArray = np.sort(flatArray)

    #Computes P90 only if at least 4 values exist
    if (len(flatArray) <= 3):
        return 0.0

    Pe=np.float(P)/100
    Percentile = flatArray[int(np.size(flatArray) * Pe)]
    return Percentile


##################################
# Mmean
#
# array = array of numbers for which to calculate the Percentile
# nodata = no data value
#
# If less than 2 values are available, the Mean is not calculated.
def Mmean(array,nodata):  
    #remove no data values, returning a flattened array  
    flatArray = array[array != nodata]
    #sorts array
    flatArray = np.sort(flatArray)

    #Computes Mean only if at least 3 values exist
    if (len(flatArray) <= 2):
        return 0.0

    LaMean = np.mean(flatArray)
    return LaMean


##############################
## P90_Mean_multiplefiles
##
## Calculation of P90, pixel by pixel, over large number of files
##
## Globals required:
## ErrorMessage, output_dir
##
## Arguments:
## filelista: full path to the list of files to be processed.
##            They must share the same grid/reference system/pixel sizes of the first one
##            in the list otherwise they are discharged
## tilesize: the size of the tiles. In principle it depends on the number of files
##           and on the available RAM (at 32 bit if python 32bit is used)
## P90_outname: the name of the TIF file with the P90 stats
## Mean_outname: the name of the TIF file with the Mean stats
## seamask: full path to a seamask, or '' if none. 0=land, 1=sea
## land_value: value to be assigned to the land pixels in the output
## nodata_value: value to be assigned to not calculated pixels
##
## Returns: - '','' if something went wrong
##          - full path of the P90 and Mean rasters (GeoTIFF)
##
def P90_Mean_multiplefiles(filelista,tilesize,P90_outname,Mean_outname,seamask,land_value,nodata_value):
    #Checks that all the files have the same size and geo-coordinates of the first one in the list
    ds=gdal.Open(filelista[0], GA_ReadOnly)
    geotrasf=ds.GetGeoTransform()
    ULx=geotrasf[0]
    ULy=geotrasf[3]
    PXx=geotrasf[1]
    PXy=geotrasf[5]
    SIZx = ds.RasterXSize
    SIZy = ds.RasterYSize
    ds=None

    for ilfile in filelista:
        try:
            ds=gdal.Open(ilfile, GA_ReadOnly)
            geotrasf=ds.GetGeoTransform()
        except RuntimeError, e:
            ErrorMessage.append(os.path.basename(ilfile)+" cannot be read ("+e+")")
            filelista[filelista.index(ilfile)]=''
            ErrorMessage.append("Removed !")
            ds=None
            continue
        except AttributeError, e:
            ErrorMessage.append(os.path.basename(ilfile)+" cannot be read ("+e+") (removed)")
            filelista[filelista.index(ilfile)]=''
            ds=None
            continue
        
        if np.abs(ULx-geotrasf[0])>0.0000001 or np.abs(ULy-geotrasf[3])>0.0000001:
            ErrorMessage.append(os.path.basename(ilfile)+" has different UL corner coordinates w.r.t. reference file "+os.path.basename(filelista[0])+" (removed)")
            filelista[filelista.index(ilfile)]=''
            ds=None
            continue
        if np.abs(PXx-geotrasf[1])>0.00001 or np.abs(PXy-geotrasf[5])>0.00001:
            ErrorMessage.append(os.path.basename(ilfile)+" has different pixel size w.r.t. reference file "+os.path.basename(filelista[0])+" (removed)")
            filelista[filelista.index(ilfile)]=''
            ds=None
            continue
        if (SIZx != ds.RasterXSize) or (SIZy != ds.RasterYSize):
            ErrorMessage.append(os.path.basename(ilfile)+" has different pixels w.r.t. reference file "+os.path.basename(filelista[0])+" (removed)")
            filelista[filelista.index(ilfile)]=''
            ds=None
            continue
        ds=None

    filelista_ind=[s for s in range(len(filelista)) if filelista[s] != '']
    if len(filelista_ind)<4:
        ErrorMessage.append("Not enough EO maps to process ("+len(filelista_ind)+")")
    filelistok=[]
    for s in filelista_ind:
        filelistok.append(filelista[s])
    filelista=filelistok
    #print "Valid images: ",len(filelistok)
    
    P90_matrix=np.zeros([SIZy,SIZx])
    Mean_matrix=np.zeros([SIZy,SIZx])
    #Read the files per tile
    nj=-1
    for j in range(0,SIZx,tilesize):
        nj=nj+1
        ni=-1
        endx=min(SIZx-j,tilesize)
        for i in range(0,SIZy,tilesize):
            ni=ni+1
            endy=min(SIZy-i,tilesize)
            #print "Leggo X:",j,endx," Leggo Y:",i,endy
            Raster_Tiles=np.zeros([len(filelista),endy,endx])
            P90_Tile=np.zeros([endy,endx])
            Mean_Tile=np.zeros([endy,endx])
            bandas=-1
            for ilfile in filelista:
                bandas=bandas+1
                ##print bandas,":",ilfile
                try:
                    ds=gdal.Open(ilfile, GA_ReadOnly)
                    band=ds.GetRasterBand(1)
                    tile_arr=band.ReadAsArray(j,i,endx,endy).astype(np.float)
                except RuntimeError, e:
                    ErrorMessage.append("Cannot read tile of"+os.path.basename(ilfile)+"("+e+")")
                    ds=None
                except AttributeError, e:
                    ErrorMessage.append("Cannot read tile of"+os.path.basename(ilfile)+"("+e+")")
                    ds=None
                else:
                    ds=None
                    nokdat=np.where(tile_arr == LandVal) #Converts LandVal to NoDataVal
                    if len(nokdat[0])>0:
                        tile_arr[nokdat]=NoDataVal
                    Raster_Tiles[bandas]=tile_arr

            for xx in range(endx):
                for yy in range(endy):
                    arra=Raster_Tiles[:,yy,xx]
                    P90_Tile[yy,xx]=np.float(Percentile(arra,90,NoDataVal))
                    Mean_Tile[yy,xx]=np.float(Mmean(arra,NoDataVal))

            P90_matrix[i:i+endy,j:j+endx]=P90_Tile
            Mean_matrix[i:i+endy,j:j+endx]=Mean_Tile

    
    if np.max(P90_matrix) == 0:
        ErrorMessage.append("For all pixels no P90 was calculated!")
        P90_file=''
    else:
        #Apply nodata_value
        nodapix=np.where(P90_matrix == 0)
        if len(nodapix[0])>0:
            P90_matrix[nodapix]=nodata_value
        
        #Save P90 statistics file
        ds=gdal.Open(filelista[0], GA_ReadOnly)
        band=ds.GetRasterBand(1)
        arr=band.ReadAsArray()
        
        [cols,rows] = arr.shape
        trans       = ds.GetGeoTransform()
        proj        = ds.GetProjection()
        arr=None
        band=None
        ds=None
        P90_file=output_dir+P90_outname

        #Reads and apply the seamask if requested
        landmask_read=0
        if len(seamask)>0:
            if os.path.exists(seamask)==False:
                ErrorMessage.append("Land mask not found: "+seamask)
            else:
                try:
                    ds=gdal.Open(seamask, GA_ReadOnly)
                    landband=ds.GetRasterBand(1)
                    landarr=landband.ReadAsArray()
                    [landcols,landrows] = landarr.shape
                except RuntimeError, e:
                    ErrorMessage.append("Error in reading land mask: "+seamask)
                else:
                    if (landcols != cols) or (landrows != rows):
                        ErrorMessage.append("Land mask ("+seamask+") raster size not compatible with products")
                    #Apply the ladmask
                    terra=np.where(landarr == 0)
                    if len(terra[0])>0:
                        landmask_read=1
                        P90_matrix[terra]=land_value

                landband=None
                landarr=None
                ds=None

        try:
            # Create the file, using the information from the original file
            outdriver = gdal.GetDriverByName("GTiff")
            outdata   = outdriver.Create(P90_file, rows, cols, 1, gdal.GDT_Float32)

            # Write the array to the file, which is the original array in this example
            outdata.GetRasterBand(1).WriteArray(P90_matrix)

            # Georeference the image
            outdata.SetGeoTransform(trans)

            # Write projection information
            outdata.SetProjection(proj)

            outdata=None
        except RuntimeError, e:
            ErrorMessage.append("Error in writing P90 GeoTIFF")
            ErrorMessage.append(e)
            P90_file=''

    if np.max(Mean_matrix) == 0:
        ErrorMessage.append("For all pixels no P90 was calculated!")
        Mean_file=''
    else:
        #Apply nodata_value
        nodapix=np.where(Mean_matrix == 0)
        if len(nodapix[0])>0:
            Mean_matrix[nodapix]=nodata_value

        #Apply the seamask if previously read and verified for the P90
        if (landmask_read==1):
            Mean_matrix[terra]=land_value

        #Save Mean statistics file
        ds=gdal.Open(filelista[0], GA_ReadOnly)
        band=ds.GetRasterBand(1)
        arr=band.ReadAsArray()
        
        [cols,rows] = arr.shape
        trans       = ds.GetGeoTransform()
        proj        = ds.GetProjection()
        arr=None
        band=None
        ds=None
        Mean_file=output_dir+Mean_outname

        try:
            # Create the file, using the information from the original file
            outdriver = gdal.GetDriverByName("GTiff")
            outdata   = outdriver.Create(Mean_file, rows, cols, 1, gdal.GDT_Float32)

            # Write the array to the file, which is the original array in this example
            outdata.GetRasterBand(1).WriteArray(Mean_matrix)

            # Georeference the image
            outdata.SetGeoTransform(trans)

            # Write projection information
            outdata.SetProjection(proj)

            outdata=None
        except RuntimeError, e:
            ErrorMessage.append("Error in writing P90 GeoTIFF")
            ErrorMessage.append(e)
            Mean_file=''

    return P90_file,Mean_file


##############################
## WQ_Stats_SAIMON
##
## Execution of the 10-days or monthly statistics procedures
##
## Globals required:
## ErrorMessage, output_dir
##
## The daily products for calculating the stats, must be located in output_dir or any of its subdirectories
##
## Input:
##        WorkingDate: a integer list [year,month,day. Day must be: 2, 12 or 22
##        stat_type: 0=10-days, 1=monthly
## Output:
##        0 = all okay, 1 = something went wrong
#
def WQ_Stats_SAIMON(WorkingDate,stat_type):

    if (stat_type != 0) and (stat_type !=1):
        ErrorMessage.append("Unknown satistics requested")
        return 1

    if (stat_type==0):
        #
        #Procedure to generate the 10-days mean
        #
        print "Calculate decade mean"
        tile_size=256
        #Identification of the 10-days period
        stopdate=datetime.date(WorkingDate[0],WorkingDate[1],WorkingDate[2])-datetime.timedelta(days=2)
        if (WorkingDate[2] == 2):
            startdate=datetime.date(WorkingDate[0],WorkingDate[1]-1,21)
            card='3rd'
        else:
            startdate=stopdate-datetime.timedelta(days=9)
            card='1st'
            if (startdate.day == 11):
                card='2nd'

        prefix='A_'+card+'_decade_'

        erro=0
        #Searches for the corresponding product files
        for el in pProds:    
            matches = []
            for root, dirnames, filenames in os.walk(prods_dir):
                for filename in fnmatch.filter(filenames, 'A*'+el+'_Num.tif'):
                    filedate=datetime.date(int(filename[1:5]),int(filename[5:7]),int(filename[7:9]))
                    if (filedate <= stopdate) and (filedate >= startdate):
                        matches.append(os.path.join(root, filename))

            #Process it only if at least 3 products are present
            if len(matches)>2:
                P90_out_name=prefix+el+'_P90_Num.tif'
                Mean_out_name=prefix+el+'_Mean_Num.tif'
                res=P90_Mean_multiplefiles(matches,tile_size,P90_out_name,Mean_out_name,SMask_LandSea,LandVal,NoDataVal)
            else:
                ErrorMessage.append("Not enough products to generate 10-days stats for "+el)
                erro=erro+1
                continue

            if len(res[0]) > 0:
                os.remove(res[0])

            if len(res[1]) == 0:
                ErrorMessage.append("10-days stats for "+el+" not generated!")
                erro=erro+1
                continue
            else:
                #Applies the legend
                lalegenda=Read_Legend(SLegends[pProds.index(el)])
                if lalegenda[0] != 0 or lalegenda[1] != 0:
                    Re,Ge,Be=Apply_Legend(res[1],-1,lalegenda)
                    lalegenda=None
                    if (len(Re[0]) > 1):
                        lres=RGB_as_input(res[1],Re,Ge,Be,output_dir+prefix+el+'_Mean_Thematic.tif')
                        Re=None
                        Ge=None
                        Be=None
                        if lres == 1:
                            ErrorMessage.append("Error in creaing thematic RGB for "+res[1])
                            erro=erro+1
                    else:
                        ErrorMessage.append("Error in applying legend to "+res[1])
                        erro=erro+1
                else:
                    ErrorMessage.append("Error in loading legend for "+res[1]+" ("+el+")")
                    erro=erro+1

        if (erro>0):
            return 1

    if (stat_type==1):
        #
        #Procedure to generate the monthly mean and P90
        #
        print "Calculate monthly P90 and Mean"
        tile_size=256
        stopdate=datetime.date(WorkingDate[0],WorkingDate[1],WorkingDate[2])-datetime.timedelta(days=2)
        erro=0
        if (WorkingDate[2] == 2):
            startdate=datetime.date(WorkingDate[0],stopdate.month,1)
            prefix='A_monthly_'

            #Searches for the corresponding product files
            for el in pProds:    
                matches = []
                for root, dirnames, filenames in os.walk(prods_dir):
                    for filename in fnmatch.filter(filenames, 'A*'+el+'_Num.tif'):
                        filedate=datetime.date(int(filename[1:5]),int(filename[5:7]),int(filename[7:9]))
                        if (filedate <= stopdate) and (filedate >= startdate):
                            matches.append(os.path.join(root, filename))

                #Process it only if at least 3 products are present
                if len(matches)>2:
                    P90_out_name=prefix+el+'_P90_Num.tif'
                    Mean_out_name=prefix+el+'_Mean_Num.tif'
                    res=P90_Mean_multiplefiles(matches,tile_size,P90_out_name,Mean_out_name,SMask_LandSea,LandVal,NoDataVal)
                else:
                    ErrorMessage.append("Not enough products to generate monthly stats for "+el)
                    erro=erro+1
                    continue

                if len(res[0])==0 and len(res[1])==0:
                    ErrorMessage.append("Monthly stats for "+el+" not generated!")
                    erro=erro+1
                    continue
                else:
                    #Applies the legends
                    lalegenda=Read_Legend(SLegends[pProds.index(el)])
                    
                    if len(res[0])==0:
                        ErrorMessage.append("Monthly P90 for "+el+" not generated!")
                        erro=erro+1
                    else:
                        #Applies the legend to P90
                        if lalegenda[0] != 0 or lalegenda[1] != 0:
                            Re,Ge,Be=Apply_Legend(res[0],-1,lalegenda)
                            if (len(Re[0]) > 1):
                                lres=RGB_as_input(res[0],Re,Ge,Be,output_dir+prefix+el+'_P90_Thematic.tif')
                                Re=None
                                Ge=None
                                Be=None
                                if lres == 1:
                                    ErrorMessage.append("Error in creaing thematic RGB for "+res[0])
                                    erro=erro+1
                            else:
                                ErrorMessage.append("Error in applying legend to "+res[0])
                                erro=erro+1
                        else:
                            ErrorMessage.append("Error in loading legend for "+res[0]+" ("+el+")")
                            erro=erro+1
                    
                    if len(res[1])==0:
                        ErrorMessage.append("Monthly mean for "+el+" not generated!")
                        erro=erro+1
                        continue
                    else:
                        #Applies the legend to Mean
                        if lalegenda[0] != 0 or lalegenda[1] != 0:
                            Re,Ge,Be=Apply_Legend(res[1],-1,lalegenda)
                            if (len(Re[0]) > 1):
                                lres=RGB_as_input(res[1],Re,Ge,Be,output_dir+prefix+el+'_Mean_Thematic.tif')
                                Re=None
                                Ge=None
                                Be=None
                                if lres == 1:
                                    ErrorMessage.append("Error in creaing thematic RGB for "+res[1])
                                    erro=erro+1
                            else:
                                ErrorMessage.append("Error in applying legend to "+res[1])
                                erro=erro+1
                        else:
                            ErrorMessage.append("Error in loading legend for "+res[1]+" ("+el+")")
                            erro=erro+1
                        
                    lalegenda=None
        else:
            ErrorMessage.append("The provided working date is not compatible with the monthly product")
            erro=erro+1

        if (erro>0):
            return 1
    
    return 0
    

#-------------------------------

if __name__ == '__main__':

    print "Main body."

    #Decade
    WkDate=[2016,05,12] #Year, month, day
    res=WQ_Stats_SAIMON(WkDate,0)
    print res
    print ErrorMessage

    #Month
    WkDate=[2016,06,2] #Year, month, day
    res=WQ_Stats_SAIMON(WkDate,1)
    print res
    print ErrorMessage
