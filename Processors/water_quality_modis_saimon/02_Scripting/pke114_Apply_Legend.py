#
# Version 2.0 of 14-01-2016
#         1.0 of 07-10-2015
#
import os
import gdal
import numpy as np
gdal.UseExceptions()


## Settings
##Needs the following variable in globals: ErrorMessage
if 'ErrorMessage' not in globals():
    ErrorMessage=[]

##
## Read_Legend
## Can read 2 types of textual legend:
## value , R, G, B
## Returns a t-uple: value, R, G, B
## In case of error returns [0,0,0,0,0]
##
def Read_Legend(legendfile):
    "Read a text legend with: value, R, G, B"
    global ErrorMessage

    if os.path.isfile(legendfile) == False:
        ErrorMessage.append("Legend file doesn't exist")
        return [0,0,0,0,0]

    color_table=[]
    #Read the text file
    try:
        fo = open(legendfile,'r')
        llines=fo.readlines()
        fo.close()
    except IOError as errore:
        ErrorMessage.append("IOError in opening legend file")
        ErrorMessage.append(str(errore))
        return [0,0,0,0]

    for line in llines:
        if line.find('#') == -1 and line.find('/') == -1 and line.find(';') == -1:
            entry = line.split()
            if len(entry) != 4:
                ErrorMessage.append("Error in legend-table line")
            else:
                color_table.extend([[float(entry[0]),int(entry[1]),int(entry[2]),int(entry[3])]])
    
    if len(color_table)<2:
        ErrorMessage.append("Legend file contains no valid lines")
        return [0,0,0,0]
                          
    return color_table

##
## Apply_Legend
##
## The legend should be a tuple: value, R, G, B
## where R-n, G-n, B-n are associated to the range value-n < x < value-n+1
## EOMap is the file to be read
## band: is not -1 then it is the band to be considered
##
## Returns a (numpy)t-uple: Red, Green Blue
## In case of error returns [[0],[0],[0]]
##
def Apply_Legend(EOMap, band, legendval):
    "Apply to a single band raster a legend (value, R, G, B)"
    global ErrorMessage

    if os.path.isfile(EOMap) == False:
        ErrorMessage.append(EOMap+" doesn't exist")
        return [[0],[0],[0]]
    try:
        data=gdal.Open(EOMap)
    except RuntimeError, e:
        ErrorMessage.append("Unable to open "+EOMap)
        return [[0],[0],[0]]

    if (band == -1) or (band <0):
        band=1

    try:
        srcband=data.GetRasterBand(band)
        if (srcband == None):
            ErrorMessage.append("Unable to get band "+str(band)+" from "+EOMap)
            return [[0],[0],[0]]
        arr=srcband.ReadAsArray()
    except RuntimeError, e:
        ErrorMessage.append("Unable to get band "+str(band)+" from "+EOMap)
        return [[0],[0],[0]]

    data=None

    Re=np.uint8(arr)
    Re.fill(0)
    Ge=np.uint8(arr)
    Ge.fill(0)
    Be=np.uint8(arr)
    Be.fill(0)

    for li in range(0,len(legendval)-1):
        ind=(arr>=legendval[li][0]) & (arr<legendval[li+1][0])
        Re[ind]=legendval[li][1]
        Ge[ind]=legendval[li][2]
        Be[ind]=legendval[li][3]

    ind=np.where(arr>=legendval[len(legendval)-1][0])
    Re[ind]=legendval[len(legendval)-1][1]
    Ge[ind]=legendval[len(legendval)-1][2]
    Be[ind]=legendval[len(legendval)-1][3]

    ind=(Re == 0) & (Ge == 0) & (Be == 0)
    if (True in ind) == True:
        ErrorMessage.append("Outlier in geophysical map")

    return Re,Ge,Be

##
## Saves a RGB raster (outgeofile) with the same gridding&geocoding of
## a reference one (outgeofile)
## Red, Gre, Blu are the RGB bands to be written
## returns 0 if okay
##
def RGB_as_input(origgeofile,Red,Gre,Blu,outgeofile):
    "Saves a RGB raster with the same gridding&geocoding of outgeofile. Red, Gre, Blu are the RGB bands to be written"
    
    # Gather some information from the original file
    data=gdal.Open(origgeofile)
    band=data.GetRasterBand(1)
    arr=band.ReadAsArray()
    
    [cols,rows] = arr.shape
    trans       = data.GetGeoTransform()
    proj        = data.GetProjection()
    data=None

    try:
        # Create the file, using the information from the original file
        outdriver = gdal.GetDriverByName("GTiff")
        outdata   = outdriver.Create(outgeofile, rows, cols, 3, gdal.GDT_Byte)

        # Write the array to the file, which is the original array in this example
        outdata.GetRasterBand(1).WriteArray(Red)
        outdata.GetRasterBand(2).WriteArray(Gre)
        outdata.GetRasterBand(3).WriteArray(Blu)

        # Georeference the image
        outdata.SetGeoTransform(trans)

        # Write projection information
        outdata.SetProjection(proj)

        outdata=None
    except RuntimeError, e:
        ErrorMessage.append("Error in writing RGB")
        ErrorMessage.append(e)

    return 0

## WHEN TESTING IS NEEDED
##if __name__ == '__main__':
##
##    print "Main body."
##
##    ##Testing parameters
##    GeoPhys_Map="F:/pke114_WQ/04_TempDir/A2016011122500.L2_LAC_OC.tif"
##    Legend_Txt="F:/pke114_WQ/01-Ancillari/Legenda_CHL.txt"
##    output_dir="F:/pke114_WQ/04_TempDir/"
##
##    lalegenda=Read_Legend(Legend_Txt)
##    if lalegenda[0] != 0 or lalegenda[1] != 0:
##        Re,Ge,Be=Apply_Legend(GeoPhys_Map,3,lalegenda)
##        if len(Re) > 1:
##            res=RGB_as_input(GeoPhys_Map,Re,Ge,Be,output_dir+"Test2.tif")
##
##    print ErrorMessage
##    print "All end."
       


        

