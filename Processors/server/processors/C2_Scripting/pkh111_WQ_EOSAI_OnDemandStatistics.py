#
# TO DO:
#
# Open issues:
# - Doesn't check for duplicates of daily products, eventuall they are all used
#
#
import os
import gdal
from gdalconst import *
import numpy as np
import datetime
import logging
import subprocess
from sys import platform as _platform
import fnmatch
import string
import random

from pke114_Apply_Legend import Read_Legend  ##Need to be in the same folder
from pke114_Apply_Legend import Apply_Legend  ##Need to be in the same folder
from pke114_Apply_Legend import RGB_as_input  ##Need to be in the same folder

############
## Pre-fixed information
##
# General
main_dir = "/src/Processors/server/processors/"
##main_dir="/home/EOSAI/"
snap = "/opt/snap/bin/gpt"

#FOR DEBUGGING ON WINDOWS
if _platform == "win32":
    main_dir="D:/pkh111_EOSAI/"
    snap="C:/Programmis/snap5/bin/gpt"

##Relative folder tree
ancil_dir = main_dir + "C1_Ancillari/"
script_dir = main_dir + "C2_Scripting/"
temp_dir = main_dir + "C4_TempDir/"
prods_dir = main_dir + "C5_OutputDir/"
global_output_dir = main_dir + "C5_OutputDir/"

###EOSAI related 
pProds = ['Chl', 'WT', 'Tur', 'SST']
SLegends = [ancil_dir + 'Legenda_CHL.txt',
            ancil_dir + 'Legenda_TR.txt',
            ancil_dir + 'Legenda_Turb.txt',
            ancil_dir + 'Legenda_SST.txt']
Mask_LandSea = [ancil_dir + "Mask_Sea-Land_SRTM_EOSAI.tif"]
Mask_GPT_Cut = [script_dir + 'SeaMask_Cut_EOSAI.xml']
AOI_Name = ['EOSAI']

###Others
IntNoData = 10000
IntNoData1 = 11000
NoDataVal = -11
LandVal = -10

GDAL_TIFF_Options_list = ['COMPRESS=LZW', 'TILED=YES']

if _platform == "linux" or _platform == "linux2":
    a = 1
else:
    ##Only for testing in Windows
    logging.basicConfig(filename=global_output_dir + 'thisismyODstat.log', filemode='w',
                        format='[EOSAI] %(asctime)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())


##################################
# Percentile
#
# array = array of numbers for which to calculate the Percentile
# P = percentile (1-100)
# nodata = no data value
#
# If less than 4 values are available, the P90 is not calculated.
def Percentile(array, P, nodata):
    # remove no data values, returning a flattened array
    flatArray = array[array != nodata]
    # sorts array
    flatArray = np.sort(flatArray)

    # Computes P90 only if at least 4 values exist
    if (len(flatArray) <= 3):
        return 0.0

    Pe = np.float(P) / 100
    Percentile = flatArray[int(np.size(flatArray) * Pe)]
    return Percentile


##################################
# Mmean
#
# array = array of numbers for which to calculate the arithmetic mean
# nodata = no data value
#
# If less than 2 values are available, the Mean is not calculated.
def Mmean(array, nodata):
    # remove no data values, returning a flattened array
    flatArray = array[array != nodata]
    # sorts array
    flatArray = np.sort(flatArray)

    # Computes Mean only if at least 3 values exist
    if (len(flatArray) <= 2):
        return 0.0

    LaMean = np.mean(flatArray)
    return LaMean


##############################
## P90_Mean_multiplefiles
##
## Calculation of P90 and arithmetic mean, pixel by pixel, over large number of files
##
##
## Arguments:
## filelista: full path to the list of files to be processed.
##            They must share the same grid/reference system/pixel sizes of the first one
##            in the list otherwise they are discharged
## tilesize: the size of the tiles. In principle it depends on the number of files
##           and on the available RAM (at 32 bit if python 32bit is used)
## P90_outname: the full path of the resulting name of the TIF file with the P90 stats
## Mean_outname: the full path of the resulting of the TIF file with the Mean stats
## seamask: full path to a seamask, or '' if none. 0=land, 1=sea
## land_value: value to be assigned to the land pixels in the output
## nodata_value: value to be assigned to not calculated pixels
##
## Returns: - '','' if something went wrong
##          - full path of the P90 and Mean rasters (GeoTIFF)
##
def P90_Mean_multiplefiles(filelista, tilesize, P90_outname, Mean_outname, seamask, land_value, nodata_value):
    # Checks that all the files have the same size and geo-coordinates of the first one in the list
    ds = gdal.Open(filelista[0], GA_ReadOnly)
    geotrasf = ds.GetGeoTransform()
    ULx = geotrasf[0]
    ULy = geotrasf[3]
    PXx = geotrasf[1]
    PXy = geotrasf[5]
    SIZx = ds.RasterXSize
    SIZy = ds.RasterYSize
    ds = None

    for ilfile in filelista:
        try:
            ds = gdal.Open(ilfile, GA_ReadOnly)
            geotrasf = ds.GetGeoTransform()
        except RuntimeError, e:
            logging.debug("[EOSAI_PROCESSORS] " + os.path.basename(ilfile) + " cannot be read (" + e + ")")
            filelista[filelista.index(ilfile)] = ''
            logging.debug("[EOSAI_PROCESSORS] " + "Removed !")
            ds = None
            continue
        except AttributeError, e:
            logging.debug("[EOSAI_PROCESSORS] " + os.path.basename(ilfile) + " cannot be read (" + e + ") (removed)")
            filelista[filelista.index(ilfile)] = ''
            ds = None
            continue

        if np.abs(ULx - geotrasf[0]) > 0.0000001 or np.abs(ULy - geotrasf[3]) > 0.0000001:
            logging.debug("[EOSAI_PROCESSORS] " + os.path.basename(
                ilfile) + " has different UL corner coordinates w.r.t. reference file " + os.path.basename(
                filelista[0]) + " (removed)")
            filelista[filelista.index(ilfile)] = ''
            ds = None
            continue
        if np.abs(PXx - geotrasf[1]) > 0.00001 or np.abs(PXy - geotrasf[5]) > 0.00001:
            logging.debug("[EOSAI_PROCESSORS] " + os.path.basename(
                ilfile) + " has different pixel size w.r.t. reference file " + os.path.basename(
                filelista[0]) + " (removed)")
            filelista[filelista.index(ilfile)] = ''
            ds = None
            continue
        if (SIZx != ds.RasterXSize) or (SIZy != ds.RasterYSize):
            logging.debug("[EOSAI_PROCESSORS] " + os.path.basename(
                ilfile) + " has different pixels w.r.t. reference file " + os.path.basename(
                filelista[0]) + " (removed)")
            filelista[filelista.index(ilfile)] = ''
            ds = None
            continue
        ds = None

    filelista_ind = [s for s in range(len(filelista)) if filelista[s] != '']
    if len(filelista_ind) < 2:
        logging.debug("[EOSAI_PROCESSORS] " + "Not enough EO maps to process (" + str(len(filelista_ind)) + ")")
        return '', ''
    filelistok = []
    for s in filelista_ind:
        filelistok.append(filelista[s])
    filelista = filelistok
    # print "Valid images: ",len(filelistok)

    P90_matrix = np.zeros([SIZy, SIZx])
    Mean_matrix = np.zeros([SIZy, SIZx])
    # Read the files per tile
    nj = -1
    for j in range(0, SIZx, tilesize):
        nj = nj + 1
        ni = -1
        endx = min(SIZx - j, tilesize)
        for i in range(0, SIZy, tilesize):
            ni = ni + 1
            endy = min(SIZy - i, tilesize)
            # print "Leggo X:",j,endx," Leggo Y:",i,endy
            Raster_Tiles = np.zeros([len(filelista), endy, endx])
            P90_Tile = np.zeros([endy, endx])
            Mean_Tile = np.zeros([endy, endx])
            bandas = -1
            for ilfile in filelista:
                bandas = bandas + 1
                ##print bandas,":",ilfile
                try:
                    ds = gdal.Open(ilfile, GA_ReadOnly)
                    band = ds.GetRasterBand(1)
                    tile_arr = band.ReadAsArray(j, i, endx, endy).astype(np.float)
                except RuntimeError, e:
                    logging.debug(
                        "[EOSAI_PROCESSORS] " + "Cannot read tile of" + os.path.basename(ilfile) + "(" + e + ")")
                    ds = None
                except AttributeError, e:
                    logging.debug(
                        "[EOSAI_PROCESSORS] " + "Cannot read tile of" + os.path.basename(ilfile) + "(" + e + ")")
                    ds = None
                else:
                    ds = None
                    nokdat = np.where(tile_arr == LandVal)  # Converts LandVal to NoDataVal
                    if len(nokdat[0]) > 0:
                        tile_arr[nokdat] = NoDataVal
                    Raster_Tiles[bandas] = tile_arr

            for xx in range(endx):
                for yy in range(endy):
                    arra = Raster_Tiles[:, yy, xx]
                    P90_Tile[yy, xx] = np.float(Percentile(arra, 90, NoDataVal))
                    Mean_Tile[yy, xx] = np.float(Mmean(arra, NoDataVal))

            P90_matrix[i:i + endy, j:j + endx] = P90_Tile
            Mean_matrix[i:i + endy, j:j + endx] = Mean_Tile

    # Reads landmask
    landmask_read = 0
    if len(seamask) > 0:
        if os.path.exists(seamask) == False:
            logging.debug("[EOSAI_PROCESSORS] " + "Land mask not found: " + seamask)
        else:
            try:
                ds = gdal.Open(seamask, GA_ReadOnly)
                landband = ds.GetRasterBand(1)
                landarr = landband.ReadAsArray()
                [landcols, landrows] = landarr.shape
            except RuntimeError, e:
                logging.debug("[EOSAI_PROCESSORS] " + "Error in reading land mask: " + seamask)
            else:
                if (landcols != SIZy) or (landrows != SIZx):
                    logging.debug(
                        "[EOSAI_PROCESSORS] " + "Land mask (" + seamask + ") raster size not compatible with products")
                else:
                    terra = np.where(landarr == 0)
                    landmask_read = 1
            landband = None
            landarr = None
            ds = None

    if np.max(P90_matrix) == 0:
        ##logging.debug("[EOSAI_PROCESSORS] "+"For all pixels no P90 was calculated!")
        P90_file = ''
    else:
        # Apply nodata_value
        nodapix = np.where(P90_matrix == 0)
        if len(nodapix[0]) > 0:
            P90_matrix[nodapix] = nodata_value

        # Save P90 statistics file
        ds = gdal.Open(filelista[0], GA_ReadOnly)
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()

        [cols, rows] = arr.shape
        trans = ds.GetGeoTransform()
        proj = ds.GetProjection()
        arr = None
        band = None
        ds = None
        P90_file = P90_outname

        # Eventually apply the seamask if requested
        if landmask_read == 1:
            # Apply the ladmask
            if len(terra[0]) > 0:
                P90_matrix[terra] = land_value

        try:
            # Create the file, using the information from the original file
            outdriver = gdal.GetDriverByName("GTiff")
            outdata = outdriver.Create(P90_file, rows, cols, 1, gdal.GDT_Float32)

            # Write the array to the file, which is the original array in this example
            outdata.GetRasterBand(1).WriteArray(P90_matrix)

            # Georeference the image
            outdata.SetGeoTransform(trans)

            # Write projection information
            outdata.SetProjection(proj)

            outdata = None
        except RuntimeError, e:
            logging.debug("[EOSAI_PROCESSORS] " + "Error in writing P90 GeoTIFF")
            logging.debug("[EOSAI_PROCESSORS] " + e)
            P90_file = ''

    if np.max(Mean_matrix) == 0:
        logging.debug("[EOSAI_PROCESSORS] " + "For all pixels no Mean was calculated!")  ## BUG FIX 23/06/2016
        Mean_file = ''
    else:
        # Apply nodata_value
        nodapix = np.where(Mean_matrix == 0)
        if len(nodapix[0]) > 0:
            Mean_matrix[nodapix] = nodata_value

        # Apply the seamask if previously read and verified for the P90
        if (landmask_read == 1):
            Mean_matrix[terra] = land_value

        # Save Mean statistics file
        ds = gdal.Open(filelista[0], GA_ReadOnly)
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()

        [cols, rows] = arr.shape
        trans = ds.GetGeoTransform()
        proj = ds.GetProjection()
        arr = None
        band = None
        ds = None
        Mean_file = Mean_outname

        try:
            # Create the file, using the information from the original file
            outdriver = gdal.GetDriverByName("GTiff")
            outdata = outdriver.Create(Mean_file, rows, cols, 1, gdal.GDT_Float32)

            # Write the array to the file, which is the original array in this example
            outdata.GetRasterBand(1).WriteArray(Mean_matrix)

            # Georeference the image
            outdata.SetGeoTransform(trans)

            # Write projection information
            outdata.SetProjection(proj)

            outdata = None
        except RuntimeError, e:
            logging.debug("[EOSAI_PROCESSORS] " + "Error in writing P90 GeoTIFF")
            logging.debug("[EOSAI_PROCESSORS] " + e)
            Mean_file = ''

    return P90_file, Mean_file


##############################
## WQ_ODStats_EOSAI
##
## Execution of the on demand statistics procedures
##
##
## The daily products for calculating the stats, must be located in prods_dir or any of its subdirectories
##
## Input:
##        WorkingDate: a list of strings yyyy-mm-dd, for startdate and enddate
##        prodflag: bit 0 -> sst
##                  bit 1 -> chl
##                  bit 2 -> wt
##                  bit 3 -> tur 
##        AOI: 1=EOSAI
##        randomchars: chars to be appended to the name of the output folder
## Output:
##        0 = all okay, 1 = something went wrong
#
def WQ_ODStats_EOSAI(
    WorkingDates,
    prodflag,
    AOI,
    randomchars):
    
    WorkingDate1 = map(int, WorkingDates[0].split("-"))
    WorkingDate2 = map(int, WorkingDates[1].split("-"))
    dest_dir = ''

    # Checks AOI
    if (AOI != 1):
        logging.info("[EOSAI_PROCESSORS] Wrong AOI parameter, set to EOSAI by default.")
        AOI = 1
    AOI = AOI - 1

    # Select requested products
    sel_pProds=[]
    if (prodflag & 1)!=0: sel_pProds.append(pProds[3])
    if (prodflag & 2)!=0: sel_pProds.append(pProds[0])
    if (prodflag & 4)!=0: sel_pProds.append(pProds[1])
    if (prodflag & 8)!=0: sel_pProds.append(pProds[2])

    if len(sel_pProds)==0:
        logging.debug("[EOSAI_PROCESSORS] No specific products requestes among the ones allowed")
        return 1, dest_dir
    logging.info("[EOSAI_PROCESSORS] Processing products: " + ', '.join(sel_pProds))

    # Cut the sea mask over the AOI
    SMask_LandSea = temp_dir + 'seamask.tif'
    commando = [snap, '-e', Mask_GPT_Cut[AOI], '-Pseamask=' + Mask_LandSea[AOI],
                '-Poutseamask=' + SMask_LandSea,
                '-Pformat=GeoTIFF+XML']
    try:
        erro = 0
        subprocess.check_call(commando)
    except subprocess.CalledProcessError:
        erro = 1

    if (erro == 1) or os.path.exists(SMask_LandSea) == None:
        logging.debug(
            "[EOSAI_PROCESSORS] Error in cutting sea mask " + Mask_LandSea[AOI] + " ! Sea mask will be not applied.")
        SMask_LandSea = ''

    if os.path.exists(SMask_LandSea[:-4] + '.xml'): os.remove(SMask_LandSea[:-4] + '.xml')
    
    #
    # Procedure to generate the mean and P90
    #
    tile_size = 256
    startdate = datetime.date(WorkingDate1[0], WorkingDate1[1], WorkingDate1[2])
    stopdate = datetime.date(WorkingDate2[0], WorkingDate2[1], WorkingDate2[2])

    if startdate >= stopdate:
        logging.debug("[EOSAI_PROCESSORS] Wrong input time period")
        if os.path.exists(SMask_LandSea): os.remove(SMask_LandSea)
        return 1, dest_dir
        
    erro = 0

    ye1 = str(startdate.year)
    me1 = str(startdate.month)
    gi1 = str(startdate.day)
    if len(me1) == 1: me1 = '0' + me1
    if len(gi1) == 1: gi1 = '0' + gi1
    prefix = 'RC_' + AOI_Name[AOI] + '_' + ye1 + me1 + gi1+'-'
    ye2 = str(stopdate.year)
    me2 = str(stopdate.month)
    gi2 = str(stopdate.day)
    if len(me2) == 1: me2 = '0' + me2
    if len(gi2) == 1: gi2 = '0' + gi2
    prefix = prefix + ye2 + me2 + gi2 + '_'

    # Searches for the corresponding product files
    for el in sel_pProds:
        matches = []
        for root, dirnames, filenames in os.walk(prods_dir):
            for filename in fnmatch.filter(filenames, 'RC_' + AOI_Name[AOI] + '*' + el + '_Num.tif'):
                filedate = datetime.datetime.strptime(filename.split("_")[2], "%Y%m%d").date()
                if (filedate <= stopdate) and (filedate >= startdate):
                    matches.append(os.path.join(root, filename))
        
        # Process it only if at least 3 products are present
        if len(matches) > 2:
            logging.info("[EOSAI_PROCESSORS] Found "+str(len(matches))+" products for "+el)
            # Creates an ad-hoc destination directory
            destprefix = ye1 + '-' + me1 + '-' + gi1 + 'to' + ye2 + '-' + me2 + '-' + gi2
            destprefix = destprefix + '_' + randomchars
            dest_dir = "%s/" % os.path.join(global_output_dir, destprefix)
            if not os.path.exists(dest_dir):
                os.mkdir(dest_dir)
            P90_out_name = dest_dir + prefix + el + '_P90_Num.tif'
            Mean_out_name = dest_dir + prefix + el + '_Mean_Num.tif'
            res = P90_Mean_multiplefiles(matches, tile_size, P90_out_name, Mean_out_name, SMask_LandSea,
                                         LandVal, NoDataVal)
        else:
            logging.debug("[EOSAI_PROCESSORS] " + "Not enough products (" + str(
                len(matches)) + ") to generate stats for " + el)
            erro = erro + 1
            if os.path.exists(dest_dir):
                os.rmdir(dest_dir)
            continue

        if len(res[0]) == 0 and len(res[1]) == 0:
            logging.debug("[EOSAI_PROCESSORS] " + "Stats for " + el + " not generated!")
            erro = erro + 1
            continue
        else:
            # Applies the legends
            loggio = []
            lalegenda = Read_Legend(SLegends[pProds.index(el)], loggio)
            for lili in loggio: logging.debug("[EOSAI_PROCESSORS] " + lili)
            if len(res[0]) == 0:
                logging.debug("[EOSAI_PROCESSORS] " + "P90 for " + el + " not generated!")
                erro = erro + 1
            else:
                # If not chlorophyll, delete it
                if el == 'Chl':
                    # Applies the legend to P90
                    if lalegenda[0] != 0 or lalegenda[1] != 0:
                        loggio = []
                        Re, Ge, Be = Apply_Legend(res[0], -1, lalegenda, loggio)
                        for lili in loggio: logging.debug("[EOSAI_PROCESSORS] " + lili)
                        if (len(Re[0]) > 1):
                            loggio = []
                            lres = RGB_as_input(res[0], Re, Ge, Be,
                                                dest_dir + prefix + el + '_P90_Thematic.tif', loggio)
                            for lili in loggio: logging.debug("[EOSAI_PROCESSORS] " + lili)
                            Re = None
                            Ge = None
                            Be = None
                            if lres == 1:
                                # Error message is already set
                                # logging.debug("[EOSAI_PROCESSORS] "+"Error in creaing thematic RGB for "+res[0])
                                erro = erro + 1
                        else:
                            # Error message is already set
                            # logging.debug("[EOSAI_PROCESSORS] "+"Error in applying legend to "+res[0])
                            erro = erro + 1
                    else:
                        # Error message is already set
                        # logging.debug("[EOSAI_PROCESSORS] "+"Error in loading legend for "+res[0]+" ("+el+")")
                        erro = erro + 1
                else:
                    os.remove(res[0])

            if len(res[1]) == 0:
                logging.debug("[EOSAI_PROCESSORS] " + "Mean for " + el + " not generated!")
                erro = erro + 1
                continue
            else:
                # Applies the legend to Mean
                if lalegenda[0] != 0 or lalegenda[1] != 0:
                    loggio = []
                    Re, Ge, Be = Apply_Legend(res[1], -1, lalegenda, loggio)
                    for lili in loggio: logging.debug("[EOSAI_PROCESSORS] " + lili)
                    if (len(Re[0]) > 1):
                        loggio = []
                        lres = RGB_as_input(res[1], Re, Ge, Be, dest_dir + prefix + el + '_Mean_Thematic.tif',
                                            loggio)
                        for lili in loggio: logging.debug("[EOSAI_PROCESSORS] " + lili)
                        Re = None
                        Ge = None
                        Be = None
                        if lres == 1:
                            # Error message is already set
                            # logging.debug("[EOSAI_PROCESSORS] "+"Error in creaing thematic RGB for "+res[1])
                            erro = erro + 1
                    else:
                        # Error message is already set
                        # logging.debug("[EOSAI_PROCESSORS] "+"Error in applying legend to "+res[1])
                        erro = erro + 1
                else:
                    # Error message is already set
                    # logging.debug("[EOSAI_PROCESSORS] "+"Error in loading legend for "+res[1]+" ("+el+")")
                    erro = erro + 1

            lalegenda = None

    if os.path.exists(SMask_LandSea): os.remove(SMask_LandSea)
    if (erro > 0):
        return 1, dest_dir

    return 0, dest_dir


############--------MAIN PROCEDURE ------------------
##########
## WQ_Stats_EOSAI_Chain
##
## Input:
##        onflag: bit 0 -> sst
##                bit 1 -> chl
##                bit 2 -> wt
##                bit 3 -> tur 
##        ovrwflag: not used
##        dates: a list with two strings: start date, end date ["yyyy-mm-dd"]. 
##        setAOI: 1=EOSAI
##
## Output: 0 okay, 1 any error
##
def WQ_OnDemandStats_EOSAI_Chain(
        onflag,
        ovrwflag,
        dates,
        setAOI=1):

    # Checks AOI
    if (setAOI != 1):
        logging.info("[EOSAI_PROCESSORS] Wrong AOI parameter, set to EOSAI by default.")
        setAOI = 1
    setAOI = setAOI - 1

    res = 0
    rnd_chars = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    
    logging.info("[EOSAI_PROCESSORS] Processing AOI: " + AOI_Name[setAOI])

    resproc, dest_dir = WQ_ODStats_EOSAI(dates, onflag, setAOI, rnd_chars)
    res = res + resproc

    return (0, dest_dir) if not res else (1, dest_dir)


# -------------------------------

if __name__ == '__main__':

    print "Main body."
    
    WkingDates=["2017-05-22","2017-05-31"]
    res=WQ_OnDemandStats_EOSAI_Chain(15,0,WkingDates)
    print res

