# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 21:39:14 2018

@author: Tom Rubino


SCRIPT 1: this script creates a study area for analysis. It uses US Census Bureau US States, USGS
Physiographic Regions, and USGS GAP Habitat data to find the habitat within a specific state and 
physiographic region. The habitat data must be obtained based on the species and area that you are 
analyzing.

In this instance, the script selects a study area based on the USGS GAP Habitat for the Eastern
Tiger Salamander that falls within the Valley and Ridge Physiographic Province in Virginia. 
The output will be further with protected habitat data, but this is done outside of the script
due to the protected status of the data. 
"""


#Import modules
import sys
from osgeo import ogr

#Import driver for shapefile. The codes can be found at http://www.gdal.org/ogr_formats.html
driver = ogr.GetDriverByName('ESRI Shapefile')

#Variables
dataFolder = r'C:\FinalCapstone\StudyArea'
#File names minus the extension
censusData = 'Census_States500k'
stateName = 'Virginia'
stateOutput = stateName + "_" + censusData

physData = 'USGS_PhysiographicRegions'
physName = 'VALLEY AND RIDGE'

physOutput = physName + "_" + physData

habitatData = 'USGSGap_HUC12_EastTigSal' #species specific so no query required

studyArea = "StudyArea_ETS"

#All data should be located in a single location.
ds = ogr.Open(dataFolder,1)   #the '1' indicates that it is writable

#If the result is 'None' it means there is an incorrect driver code as the 
if ds is None:
    print "Open failed. Please check that appropriate driver is added./n"
    sys.exit(1)

#Query the national datasets to limit the study area    

#Select the state of virginia from the census states layer
stateInput = ds.GetLayer(censusData)
stateInput.SetAttributeFilter("NAME = " +  stateName)
#stateInput.SetAttributeFilter("NAME = 'Virginia'") #ready to delete
ds.CopyLayer(stateInput, stateOutput)

#Select the valley and ridge physiographic region - it works
physInput = ds.GetLayer(physData)
physInput.SetAttributeFilter("PROVINCE = " + physName)
ds.CopyLayer(physInput, physOutput)

#Retrieve each layer based on the file name in the folder
stateGet = ds.GetLayer(stateOutput) #formerly vastate_in
physGet = ds.GetLayer(physOutput) #formerly vrphys_in
habitatGet = ds.GetLayer(habitatData) #formerly gaphab_in

#Intersection of the valley ridge phys that falls within virginia
vrphys_va = ds.CreateLayer('vrphys_va_intersect',physGet.GetSpatialRef(),ogr.wkbPolygon)
vrphys_int = stateGet.Intersection(physGet, vrphys_va)
vrphys_out = ds.GetLayer('vrphys_va_intersect')

#Intersection of the ets gap hab that falls within virginia
gaphab_va = ds.CreateLayer('gaphab_va_intersect',habitatGet.GetSpatialRef(),ogr.wkbPolygon)
gaphab_int = stateGet.Intersection(habitatGet, gaphab_va)
gaphab_out = ds.GetLayer('gaphab_va_intersect')

#intersection of the gap hab that falls within the ridge valley physio within virginia
#may want to make this a spatial filter, though.
gaphab_vrphys_va = ds.CreateLayer(studyArea ,habitatGet.GetSpatialRef(),ogr.wkbMultiPolygon)
gaphab_vrphys_int = vrphys_out.Intersection(gaphab_out, gaphab_vrphys_va)
gaphab_vrphys_out = ds.GetLayer(studyArea)

del ds

print "SCRIPT COMPLETE!"

