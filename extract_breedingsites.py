# -*- coding: utf-8 -*-
'''
Created on Wed Aug 22 22:15:05 2018

@author: tom

This script extracts the wetlands used to model breeding sites
for the Eastern Tiger Salamander
'''

import sys
import ogr

#Import driver
driver = ogr.GetDriverByName('ESRI Shapefile')

ds = ogr.Open(r'C:\FinalCapstone\Wetlands',1)
wetlands_ln = 'VA_Wetlands_3968'

#If you get None it means there is an incorrect driver code
if ds is None:
    print "Open failed./n"
    sys.exit(1)

#Query wetlands used for breeding site modeling
wetlands_in = ds.GetLayer('VA_Wetlands_3968')
wetlands_in.SetAttributeFilter("((WETLAND_TY = 'Freshwater Emergent Wetland') OR (WETLAND_TY = 'Freshwater Forested/Shrub Wetland') OR (WETLAND_TY = 'Freshwater Pond'))")
wltype_fld = ogr.FieldDefn('FRAGMENT',ogr.OFTString)
wltype_fld.SetWidth(10)
wetlands_in.CreateField(ogr.FieldDefn('FRAGMENT',ogr.OFTString))
for feat in wetlands_in:
    feat.SetField('FRAGMENT','No')
    wetlands_in.SetFeature(feat)

wetlands_out = ds.CopyLayer(wetlands_in, 'BreedingSites')

ds = None

print ("SCRIPT COMPLETE!")


