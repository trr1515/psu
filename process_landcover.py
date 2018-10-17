# -*- coding: utf-8 -*-
'''
Created on Sun Aug 12 11:31:03 2018
@author: tom

This script reclassified landcover based on the defined list.

The input is a mosaicked landcover raster clipped to the study area.

This can be accomplished with GIS software or GDAL.

'''


#Reclassify landcover
import os
from osgeo import ogr, gdal
import numpy as np

driver = gdal.GetDriverByName('GTiff')
folder = r'C:\FinalCapstone\Landcover'
shp_ds = ogr.Open(folder)

os.chdir(r'C:\FinalCapstone\Landcover')
lcRaster = 'lc_mosaic_cutline.tif'

in_ds = gdal.Open(lcRaster)
in_band = in_ds.GetRasterBand(1)

studyarea_ln = 'studyareaETS_3968'

list_data = in_band.ReadAsArray()

#Reclassification 
list_des = list_data.copy()

#Landcover reclassification values
print "reclassifying array"
list_des[np.where(list_data == 11)] = 50
list_des[np.where(list_data == 21)] = 90
list_des[np.where(list_data == 22)] = 90
list_des[np.where(list_data == 31)] = 60
list_des[np.where(list_data == 41)] = 0
list_des[np.where(list_data == 42)] = 0
list_des[np.where(list_data == 51)] = 20
list_des[np.where(list_data == 61)] = 50
list_des[np.where(list_data == 71)] = 40
list_des[np.where(list_data == 81)] = 50
list_des[np.where(list_data == 82)] = 70
list_des[np.where(list_data == 91)] = 10
print "reclassifying array complete"                      
            
#Create new file

file2 = driver.Create('LandcoverFinal.tif', in_ds.RasterXSize , in_ds.RasterYSize , 1)
file2.GetRasterBand(1).WriteArray(list_des)

#Spatial reference system
proj = in_ds.GetProjection()
georef = in_ds.GetGeoTransform()
file2.SetProjection(proj)
file2.SetGeoTransform(georef)
file2.FlushCache()

print "new landcover created..."