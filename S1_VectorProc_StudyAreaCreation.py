# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 11:21:34 2018

@author: tom
"""

import sys
import gdal
#the ogr module lives inside the osgeo package which was installed with python bindings for gdal
from osgeo import ogr

# import driver for shapefile. The codes can be found at http://www.gdal.org/ogr_formats.html
driver = ogr.GetDriverByName('ESRI Shapefile')
#print (driver)

#variables for original dataset processing
#national datasets
us_states = r'C:\PSU\ScriptData\Census_States500k'
us_physregions = r'C:\PSU\ScriptData\USGS_PhysiographicRegions'
us_gaphab_ets = r'C:\PSU\ScriptData\USGSGap_HUC12_EastTigSal'
#local datasets
va_roads = r'C:\PSU\ScriptData\Centerline_VA_Basemapping_program_3969'
va_wetlands = r'C:\PSU\ScriptData\VA_Wetlands'
studyarea_small = r'C:\PSU\ScriptData\ets_ssa_final_valam'

#get virginia from all states
#pg104. 



#all data is located in ScriptData
ds = ogr.Open(r'C:\PSU\ScriptData',1)

# if you get None it means there is an incorrect driver code. You should get the object type returned
if ds is None:
    print "Open failed./n"
    sys.exit(1)

#this selects the state of virginia from the census states layer - it works
state_in = ds.GetLayer('Census_States500k')
state_in.SetAttributeFilter("NAME = 'Virginia'")
state_out = ds.CopyLayer(state_in, 'Virginia_extracted')

#this selects the valley and ridge physiographic region - it works
phys_in = ds.GetLayer('USGS_PhysiographicRegions')
phys_in.SetAttributeFilter("PROVINCE = 'VALLEY AND RIDGE'")
phys_out = ds.CopyLayer(phys_in, 'ValleyAndRidge_extracted')

#this selects breeding sites for the eastern tiger salamander - it works
breed_in = ds.GetLayer('VA_Wetlands')
breed_in.SetAttributeFilter("WETLAND_TY = 'Freshwater Emergent Wetland' OR WETLAND_TY = 'Freshwater Forested/Shrub Wetland'")
breed_out = ds.CopyLayer(breed_in, 'Wetlands_breeding_extracted')

#break out the roads based on type - this works, but need to populate these records as one way or divided
roads_in = ds.GetLayer('Centerline_VA_Basemapping_program_3969')
roads_in.SetAttributeFilter("(ONE_WAY = 'FT' OR ONE_WAY = 'TF') OR (DUAL_CARRI = 'Y')")
divrd_out = ds.CopyLayer(roads_in, 'Divided_roads_extracted')
# clear previous attribute selection filter by passing None
ds.GetLayer().SetAttributeFilter(None) 

#highway roads
roads_in.SetAttributeFilter("(LOCAL_SPEE >= 55) AND (RD_TYPE IS NOT 'Divided/Dual-Carriageway')")
hwyrd_out = ds.CopyLayer(roads_in, 'Highway')

#primary roads
roads_in.SetAttributeFilter("(LOCAL_SPEE >=35) AND (LOCAL_SPEE <55) AND (RD_TYPE IS NOT  'Divided/Dual-Carriageway')")
prird_out = ds.CopyLayer(roads_in, 'Primary')

#secondary roads
roads_in.SetAttributeFilter("(LOCAL_SPEE >20) AND (LOCAL_SPEE <35) AND (RD_TYPE IS NOT  'Divided/Dual-Carriageway')")
secrd_out = ds.CopyLayer(roads_in, 'Secondary')

#tertiary roads
roads_in.SetAttributeFilter("(LOCAL_SPEE >=20) AND (RD_TYPE IS NOT  'Divided/Dual-Carriageway')")
terrd_out = ds.CopyLayer(roads_in, 'Tertiary')



#add road type field to 
#set field definition for adding new text fields
div_roads = ds.GetLayer('Divided_roads_extracted')
rdtype_fld = ogr.FieldDefn('RD_TYPE',ogr.OFTString)
rdtype_fld.SetWidth(50)
div_roads.CreateField(ogr.FieldDefn('RD_TYPE',ogr.OFTString))
for feat in div_roads:
    feat.SetField('RD_TYPE','Divided/Dual Carriageway')
    div_roads.SetFeature(feat)




del ds

