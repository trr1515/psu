# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 11:21:34 2018

@author: tom
"""

import sys
#the ogr module lives inside the osgeo package which was installed with python bindings for gdal
from osgeo import ogr
from shapely.geometry import Polygon
from shapely.ops import cascaded_union


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

vastate_in = ds.GetLayer('Virginia_extracted')
vrphys_in = ds.GetLayer('ValleyAndRidge_extracted')
gaphab_in = ds.GetLayer('USGSGap_HUC12_EastTigSal')

#intersection of the valley ridge phys that falls within virginia
vrphys_va = ds.CreateLayer('vrphys_va_intersect',vrphys_in.GetSpatialRef(),ogr.wkbPolygon)
vrphys_int = vastate_in.Intersection(vrphys_in, vrphys_va)
vrphys_out = ds.GetLayer('vrphys_va_intersect')

#intersection of the ets gap hab that falls within virginia - may not be a necessary step, though.
gaphab_va = ds.CreateLayer('gaphab_va_intersect',gaphab_in.GetSpatialRef(),ogr.wkbPolygon)
gaphab_int = vastate_in.Intersection(gaphab_in, gaphab_va)
gaphab_out = ds.GetLayer('gaphab_va_intersect')

#intersection of the gap hab that falls within the ridge valley physio within virginia
#may want to make this a spatial filter, though.
gaphab_vrphys_va = ds.CreateLayer('gaphab_vrphys_intersect',gaphab_in.GetSpatialRef(),ogr.wkbMultiPolygon)
gaphab_vrphys_int = vrphys_out.Intersection(gaphab_out, gaphab_vrphys_va)
gaphab_vrphys_out = ds.GetLayer('gaphab_vrphys_intersect')

#dissolve the results - aggregation - cascaded unions

multipoly = ogr.Geometry(ogr.wkbMultiPolygon).CreateLayer()
outputsy = gaphab_vrphys_out.SetSpatialFilter(multipoly.UnionCascaded())

print outputsy

#clip the output to the eoreps to only include gaphab that intersects





#add a buffer











#create layer with virginia's valley and ridge phys region - ValleyAndRidge_extracted clipped with Virginia_extracted

#pg 55 - create a new layer to store your output data in. 
#CreateLayer(name, [srs], [geom_type], [options])







#this selects breeding sites for the eastern tiger salamander - it works
#wetlandsbreed_in = ds.GetLayer('Wetlands_breeding_extracted')
#breed_in.SetAttributeFilter("WETLAND_TY = 'Freshwater Emergent Wetland' OR WETLAND_TY = 'Freshwater Forested/Shrub Wetland'")
#breed_out = ds.CopyLayer(breed_in, 'Wetlands_breeding_extracted')



print "ok doneski"
del ds