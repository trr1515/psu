# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 22:15:05 2018

@author: tom
"""

#this script processes the Virginia state roads from the being a statewide
#dataset, to a weighted raster representing different types of roads and
#the distance to each.

import sys
import os
from osgeo import gdal, ogr
import numpy as np


# import driver for shapefile. The codes can be found at http://www.gdal.org/ogr_formats.html
driver = ogr.GetDriverByName('ESRI Shapefile')

#all data is located in ScriptData
ds = ogr.Open(r'C:\PSU\WetlandsData',1)
wetlands_ln = 'VA_Wetlands_3968'

# if you get None it means there is an incorrect driver code. You should get the object type returned
if ds is None:
    print "Open failed./n"
    sys.exit(1)



#query and attribute primary roads
roads_in = ds.GetLayer('VA_Wetlands_3968')
roads_in.SetAttributeFilter("((WETLAND_TY = 'Freshwater Emergent Wetland') OR (WETLAND_TY = 'Freshwater Forested/Shrub Wetland') OR (WETLAND_TY = 'Freshwater Pond'))")
rdtype_fld = ogr.FieldDefn('FRAGMENT',ogr.OFTString)
rdtype_fld.SetWidth(10)
roads_in.CreateField(ogr.FieldDefn('FRAGMENT',ogr.OFTString))
for feat in roads_in:
    feat.SetField('FRAGMENT','No')
    roads_in.SetFeature(feat)

prird_out = ds.CopyLayer(roads_in, 'BreedingSites')



ds = None


print ("Done")


