# -*- coding: utf-8 -*-
"""
Created on Sun Aug 12 11:31:03 2018

@author: tom
"""

#reclassify landcover

import os
from osgeo import gdal
import numpy as np

driver = gdal.GetDriverByName('GTiff')


os.chdir(r'C:\PSU\ScriptRaster')
lcRaster = 'lc.tif'

in_ds = gdal.Open(lcRaster)
in_band = in_ds.GetRasterBand(1)




list_data = in_band.ReadAsArray()

# reclassification 
print
list_des = list_data.copy()


print "reclassifying array"
list_des[np.where(list_data == 11)] = 50
list_des[np.where(list_data == 21)] = 90
list_des[np.where(list_data == 22)] = 90
list_des[np.where(list_data == 31)] = 50
list_des[np.where(list_data == 41)] = 0
list_des[np.where(list_data == 42)] = 0
list_des[np.where(list_data == 51)] = 20
list_des[np.where(list_data == 61)] = 60
list_des[np.where(list_data == 71)] = 40
list_des[np.where(list_data == 81)] = 50
list_des[np.where(list_data == 82)] = 60
list_des[np.where(list_data == 91)] = 20
print "reclassifying array complete"                      
            
# create new file
# create new file
file2 = driver.Create('reclassifed_lc.tif', in_ds.RasterXSize , in_ds.RasterYSize , 1)
file2.GetRasterBand(1).WriteArray(list_des)

# spatial ref system
proj = in_ds.GetProjection()
georef = in_ds.GetGeoTransform()
file2.SetProjection(proj)
file2.SetGeoTransform(georef)
file2.FlushCache()

print "new landcover created..."
  
print "reprojecting"          
rp_output = r"C:\PSU\ScriptRaster"
rp_input = gdal.Open(rp_output)
rp_output = r"C:\PSU\ScriptRaster\reclass_lc_rp"
gdal.Warp(rp_output,rp_input,dstSRS='EPSG:3968')
print "and now all done!"