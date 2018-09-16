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
ds = ogr.Open(r'C:\PSU\RoadData',1)

# if you get None it means there is an incorrect driver code. You should get the object type returned
if ds is None:
    print "Open failed./n"
    sys.exit(1)
    
roadTypeList = []

#reproject the virginia basemapping project road data into CRS: 3969
#  this should only need to be done for the state wide dataset
#  here

# Create variables

#divide the road types so that each can be weighted and scored separately
#based on whether it is divided or not, and the speed limit. This process
#is processing state wide data, until the next step when it will limit the
#area based on the derived study area.

#break out the roads based on type
roads_in = ds.GetLayer('Centerline_VA_Basemapping_program_3969')
roads_in.SetAttributeFilter("(ONE_WAY = 'FT' OR ONE_WAY = 'TF') OR (DUAL_CARRI = 'Y')")
#add Road Type field 
rdtype_fld = ogr.FieldDefn('RD_TYPE',ogr.OFTString)
rdtype_fld.SetWidth(50)
roads_in.CreateField(ogr.FieldDefn('RD_TYPE',ogr.OFTString))
for feat in roads_in:
    feat.SetField('RD_TYPE','Carriageway')
    roads_in.SetFeature(feat)

#copy of selected and attributed divided roads/carriageways
divrd_out = ds.CopyLayer(roads_in, 'Roads_Divided_Vec')
roadTypeList.append('Roads_Divided_Vec')
print roadTypeList
#clear selection
ds.GetLayer('Centerline_VA_Basemapping_program_3969').SetAttributeFilter(None) 
#query and attribute highways
roads_in.SetAttributeFilter("(LOCAL_SPEE >= 55) AND NOT (RD_TYPE = 'Carriageway')")
for feat in roads_in:
    feat.SetField('RD_TYPE','Highway')
    roads_in.SetFeature(feat)
hwyrd_out = ds.CopyLayer(roads_in, 'Roads_Highway_Vec')
roadTypeList.append('Roads_Highway_Vec')
print roadTypeList
ds.GetLayer('Centerline_VA_Basemapping_program_3969').SetAttributeFilter(None) 

#query and attribute primary roads
roads_in.SetAttributeFilter("((LOCAL_SPEE >=35) AND (LOCAL_SPEE <55)) AND NOT (RD_TYPE = 'Carriageway')")
for feat in roads_in:
    feat.SetField('RD_TYPE','Primary')
    roads_in.SetFeature(feat)
prird_out = ds.CopyLayer(roads_in, 'Roads_Primary_Vec')
roadTypeList.append('Roads_Primary_Vec')
print roadTypeList
ds.GetLayer('Centerline_VA_Basemapping_program_3969').SetAttributeFilter(None)

#query and attribute secondary roads
roads_in.SetAttributeFilter("((LOCAL_SPEE >20) AND (LOCAL_SPEE <35)) AND NOT (RD_TYPE = 'Carriageway')")
for feat in roads_in:
    feat.SetField('RD_TYPE','Secondary')
    roads_in.SetFeature(feat)
secrd_out = ds.CopyLayer(roads_in, 'Roads_Secondary_Vec')
roadTypeList.append('Roads_Secondary_Vec')
print roadTypeList
ds.GetLayer('Centerline_VA_Basemapping_program_3969').SetAttributeFilter(None)

#query and attribute tertiary roads
roads_in.SetAttributeFilter("(LOCAL_SPEE <=20) AND NOT (RD_TYPE = 'Carriageway')")
for feat in roads_in:
    feat.SetField('RD_TYPE','Tertiary')
    roads_in.SetFeature(feat)
terrd_out = ds.CopyLayer(roads_in, 'Roads_Tertiary_Vec')
roadTypeList.append('Roads_Tertiary_Vec')
print roadTypeList
ds.GetLayer('Centerline_VA_Basemapping_program_3969').SetAttributeFilter(None)

ds = None
print "Road vectors have been successfully extracted."


# Script to use proximity analysis and compute mean distance
# from roads.

folder = r'C:\PSU\RoadData'
studyarea_ln = 'studyareaETS_3968'


# Set the cell size for the analysis.
cellsize = 10

shp_ds = ogr.Open(folder)


# Get the extent of the wilderness area.
wild_lyr = shp_ds.GetLayerByName(studyarea_ln)
#wild_lyr.SetAttributeFilter("NAME_1_1 = 'Meadow Run'") #study area can go here
#wild_lyr.SetAttributeFilter("WILD_NM = 'Frank Church - RONR'")
envelopes = [row.geometry().GetEnvelope() for row in wild_lyr]
coords = list(zip(*envelopes))
minx, maxx = min(coords[0]), max(coords[1])
miny, maxy = min(coords[2]), max(coords[3])

# Select the roads that fall within the wilderness extent.

for rd in roadTypeList:
    os.chdir(folder)
    tif_driver = gdal.GetDriverByName('GTiff')
    road_lyr = shp_ds.GetLayerByName(rd)
    road_lyr.SetSpatialFilterRect(minx, miny, maxx, maxy)
    
    # Figure out the output size.
    cols = int((maxx - minx) / cellsize)
    rows = int((maxy - miny) / cellsize)


    # Create an empty raster to hold the rasterized roads.
    road_raster_fn = rd + '.tif'  
    road_ds = tif_driver.Create(road_raster_fn, cols, rows)
    road_ds.SetProjection(road_lyr.GetSpatialRef().ExportToWkt())
    road_ds.SetGeoTransform((minx, cellsize, 0, maxy, 0, -cellsize))

    # Burn the roads into the raster.
    gdal.RasterizeLayer(
            road_ds, [1], road_lyr, burn_values=[1],
            callback=gdal.TermProgress)

    # Burn proximity to roads into a new raster.
    proximity_fn = rd + '_Prox.tif'
    prox_ds = tif_driver.Create(proximity_fn, cols, rows, 1, gdal.GDT_Int32)
    prox_ds.SetProjection(road_ds.GetProjection())
    prox_ds.SetGeoTransform(road_ds.GetGeoTransform())
    gdal.ComputeProximity(
            road_ds.GetRasterBand(1), prox_ds.GetRasterBand(1),
            ['DISTUNITS=GEO'], gdal.TermProgress)

    # Burn the wilderness area into a temporary raster.
    wild_ds = gdal.GetDriverByName('MEM').Create('tmp', cols, rows)
    wild_ds.SetProjection(prox_ds.GetProjection())
    wild_ds.SetGeoTransform(prox_ds.GetGeoTransform())
    gdal.RasterizeLayer(
            wild_ds, [1], wild_lyr, burn_values=[1],
            callback=gdal.TermProgress)

    # Use the temporary wilderness raster to set the proximity one
    # to NoData everywhere that is outside the wilderness area.
    wild_data = wild_ds.ReadAsArray()
    prox_data = prox_ds.ReadAsArray()
    prox_data[wild_data == 0] = -99
    prox_ds.GetRasterBand(1).WriteArray(prox_data)
    prox_ds.GetRasterBand(1).SetNoDataValue(-99)
    prox_ds.FlushCache()

    # Compute statistics and calculate the mean distance to roads,
    # which is just the mean value of the proximity raster.
    stats = prox_ds.GetRasterBand(1).ComputeStatistics(
            False, gdal.TermProgress)
    print('Mean distance from ' + rd + ' roads is', stats[2])


  #RECLASSIFICATION   
    
    print ("Reclassifying " + rd)
    os.chdir(r'C:\PSU\RoadData')
    output_rd_ds = rd + '_Prox_RC.tif'

    in_ds = gdal.Open(proximity_fn)
    in_band = in_ds.GetRasterBand(1)

    list_data = in_band.ReadAsArray()

   
    list_des = list_data.copy()
    
    Roads_Divided_Vec_List = [100,90,70,50,0]
    Roads_Highway_Vec_List = [100,80,60,40,0]
    Roads_Primary_Vec_List = [80,60,40,20,0]
    Roads_Secondary_Vec_List = [60,40,20,10,0]
    Roads_Tertiary_Vec_List = [40,20,10,5,0]
    
    if 'Divided' in rd:        
        print ("Reclassifying " + rd)
        list_des[np.where( list_data <= 50 )] = Roads_Divided_Vec_List[0]
        list_des[np.where((50 < list_data) & (list_data <= 300)) ] = Roads_Divided_Vec_List[1]
        list_des[np.where((300 < list_data) & (list_data <= 600)) ] = Roads_Divided_Vec_List[2]
        list_des[np.where((600 < list_data) & (list_data <= 1000)) ] = Roads_Divided_Vec_List[3]
        list_des[np.where( list_data > 1000 )] = Roads_Divided_Vec_List[4]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_rd_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + rd + " raster successfully reclassified."
    if 'Highway' in rd:
        print ("Reclassifying " + rd)
        list_des[np.where( list_data <= 50 )] = Roads_Highway_Vec_List[0]
        list_des[np.where((50 < list_data) & (list_data <= 300)) ] = Roads_Highway_Vec_List[1]
        list_des[np.where((300 < list_data) & (list_data <= 600)) ] = Roads_Highway_Vec_List[2]
        list_des[np.where((600 < list_data) & (list_data <= 1000)) ] = Roads_Highway_Vec_List[3]
        list_des[np.where( list_data > 1000 )] = Roads_Highway_Vec_List[4]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_rd_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + rd + " raster successfully reclassified."
    if 'Primary' in rd:
        print ("Reclassifying " + rd)
        list_des[np.where( list_data <= 50 )] = Roads_Primary_Vec_List[0]
        list_des[np.where((50 < list_data) & (list_data <= 300)) ] = Roads_Primary_Vec_List[1]
        list_des[np.where((300 < list_data) & (list_data <= 600)) ] = Roads_Primary_Vec_List[2]
        list_des[np.where((600 < list_data) & (list_data <= 1000)) ] = Roads_Primary_Vec_List[3]
        list_des[np.where( list_data > 1000 )] = Roads_Primary_Vec_List[4]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_rd_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + rd + " raster successfully reclassified."
    if 'Secondary' in rd:
        print ("Reclassifying " + rd)
        list_des[np.where( list_data <= 50 )] = Roads_Secondary_Vec_List[0]
        list_des[np.where((50 < list_data) & (list_data <= 300)) ] = Roads_Secondary_Vec_List[1]
        list_des[np.where((300 < list_data) & (list_data <= 600)) ] = Roads_Secondary_Vec_List[2]
        list_des[np.where((600 < list_data) & (list_data <= 1000)) ] = Roads_Secondary_Vec_List[3]
        list_des[np.where( list_data > 1000 )] = Roads_Secondary_Vec_List[4]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_rd_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + rd + " raster successfully reclassified."
    if 'Tertiary' in rd:
        print ("Reclassifying " + rd)
        list_des[np.where( list_data <= 50 )] = Roads_Tertiary_Vec_List[0]
        list_des[np.where((50 < list_data) & (list_data <= 300)) ] = Roads_Tertiary_Vec_List[1]
        list_des[np.where((300 < list_data) & (list_data <= 600)) ] = Roads_Tertiary_Vec_List[2]
        list_des[np.where((600 < list_data) & (list_data <= 1000)) ] = Roads_Tertiary_Vec_List[3]
        list_des[np.where( list_data > 1000 )] = Roads_Tertiary_Vec_List[4]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_rd_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + rd + " raster successfully reclassified."
    else:
        continue


#driver = gdal.GetDriverByName('GTiff')
print ("Merging reclassified road rasters into final scored output.....")
os.chdir(r'C:\PSU\RoadData')
divrd_ds = 'Roads_Divided_Vec_Prox_RC.tif'
hwyrd_ds = 'Roads_Highway_Vec_Prox_RC.tif'
prird_ds = 'Roads_Primary_Vec_Prox_RC.tif'
secrd_ds = 'Roads_Secondary_Vec_Prox_RC.tif'
terrd_ds = 'Roads_Tertiary_Vec_Prox_RC.tif'

output_rd_ds = 'RoadsFinalMerge.tif'

divrd_in = gdal.Open(divrd_ds)
divrd_band = divrd_in.GetRasterBand(1)
divrd_list = divrd_band.ReadAsArray()

hwyrd_in = gdal.Open(hwyrd_ds)
hwyrd_band = hwyrd_in.GetRasterBand(1)
hwyrd_list = hwyrd_band.ReadAsArray()

prird_in = gdal.Open(prird_ds)
prird_band = prird_in.GetRasterBand(1)
prird_list = prird_band.ReadAsArray()

secrd_in = gdal.Open(secrd_ds)
secrd_band = secrd_in.GetRasterBand(1)
secrd_list = secrd_band.ReadAsArray()

terrd_in = gdal.Open(terrd_ds)
terrd_band = terrd_in.GetRasterBand(1)
terrd_list = terrd_band.ReadAsArray()


#create maximum numpy arrays. there is a maximum so compare two, compare results, and continue
hd_out = np.maximum(divrd_list,hwyrd_list)
hdp_out = np.maximum(hd_out, prird_list)
hdps_out = np.maximum(hdp_out, secrd_list)
hdpst_out = np.maximum(hdps_out, terrd_list)
print (".....Road rasters merged based on maximum value")

print hdpst_out

file2 = tif_driver.Create(output_rd_ds, divrd_in.RasterXSize , divrd_in.RasterYSize , 1)
file2.GetRasterBand(1).WriteArray(hdpst_out)

# spatial ref system
proj = divrd_in.GetProjection()
georef = divrd_in.GetGeoTransform()
file2.SetProjection(proj)
file2.SetGeoTransform(georef)
file2.FlushCache()

divrd_ds = None
hwyrd_ds = None
prird_ds = None
secrd_ds = None
terrd_ds = None
prox_ds = None
road_ds = None
shp_ds = None

print "SCRIPT COMPLETE"
