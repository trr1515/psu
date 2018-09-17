# -*- coding: utf-8 -*-
"""
Created on Tue Sep 04 23:31:41 2018

@author: tom
"""

'''
This script takes a statewide USGS Wetlands dataset and breaks it down based on the type
of wetland, rasterizes, and reclassifies into a single raster.
'''


import os
import sys
from osgeo import gdal, ogr
import numpy as np

# import driver for shapefile. The codes can be found at http://www.gdal.org/ogr_formats.html
driver = ogr.GetDriverByName('ESRI Shapefile')
tif_driver = gdal.GetDriverByName('GTiff')

#all data is located in ScriptData
ds = ogr.Open(r'C:\PSU\WetlandsData',1)

# if you get None it means there is an incorrect driver code. You should get the object type returned
if ds is None:
    print "Open failed./n"
    sys.exit(1)

#reproject the virginia basemapping project road data into CRS: 3969

folder = r'C:\PSU\WetlandsData'
wetlands_ln = 'VA_Wetlands_3968'
studyarea_ln = 'studyareaETS_3968'
#road_raster_fn = 'wetlands_ras.tif'
#proximity_fn = 'wetlands_proximity.tif'


wetlandTypeList = []

#wlType = 'Lake'

#wetlands_ln = 'Wetlands_' + wlType
#raster_fn = 'Wetlands_' + wlType + '.tif'
#prox_fn = 'Wetlands_' + wlType + '_Prox.tif'

# Set the cell size for the analysis.
cellsize = 10

#divide the road types so that each can be weighted and scored separately
#based on whether it is divided or not, and the speed limit. This process
#is processing state wide data, until the next step when it will limit the
#area based on the derived study area.
    
#The other wetland types are 'Estuarine and Marine Deepwater' and
#'Estuarine and Marine Wetland' but they are left out due to the non-coastal
#study area


#break out the wetlands based on type

#Lake
wetlands_in = ds.GetLayer(wetlands_ln)
wetlands_in.SetAttributeFilter("(WETLAND_TY = 'Lake')")
#copy of selected and attributed divided roads/carriageways
lake_out = ds.CopyLayer(wetlands_in, 'Wetlands_Lake')
wetlandTypeList.append('Wetlands_Lake')
print wetlandTypeList
ds.GetLayer(wetlands_ln).SetAttributeFilter(None) 
print ("Lake extracted from Wetlands")

#Freshwater Emergent Wetland
wetlands_in = ds.GetLayer(wetlands_ln)
wetlands_in.SetAttributeFilter("(WETLAND_TY = 'Freshwater Emergent Wetland')")
#copy of selected and attributed divided roads/carriageways
fresh_emerg_out = ds.CopyLayer(wetlands_in, 'Wetlands_FreshwaterEmergent')
wetlandTypeList.append('Wetlands_FreshwaterEmergent')
print wetlandTypeList
ds.GetLayer(wetlands_ln).SetAttributeFilter(None) 
print ("Freshwater Emergent Wetland extracted from Wetlands")

#Freshwater Forested/Shrub Wetland
wetlands_in = ds.GetLayer(wetlands_ln)
wetlands_in.SetAttributeFilter("(WETLAND_TY = 'Freshwater Forested/Shrub Wetland')")
#copy of selected and attributed divided roads/carriageways
fresh_forest_out = ds.CopyLayer(wetlands_in, 'Wetlands_FreshwaterForested')
wetlandTypeList.append('Wetlands_FreshwaterForested')
print wetlandTypeList
ds.GetLayer(wetlands_ln).SetAttributeFilter(None) 
print ("Freshwater Forested/Shrub Wetland extracted from Wetlands")

#Riverine
wetlands_in = ds.GetLayer(wetlands_ln)
wetlands_in.SetAttributeFilter("(WETLAND_TY = 'Riverine')")
#copy of selected and attributed divided roads/carriageways
riverine_out = ds.CopyLayer(wetlands_in, 'Wetlands_Riverine')
wetlandTypeList.append('Wetlands_Riverine')
print wetlandTypeList
ds.GetLayer(wetlands_ln).SetAttributeFilter(None) 
print ("Riverine extracted from Wetlands")

#Freshwater Pond
wetlands_in = ds.GetLayer(wetlands_ln)
wetlands_in.SetAttributeFilter("(WETLAND_TY = 'Freshwater Pond')")
#copy of selected and attributed divided roads/carriageways
pond_out = ds.CopyLayer(wetlands_in, 'Wetlands_FreshwaterPond')
wetlandTypeList.append('Wetlands_FreshwaterPond')
print wetlandTypeList
ds.GetLayer(wetlands_ln).SetAttributeFilter(None) 
print ("Freshwater Pond extracted from Wetlands")

#Other
wetlands_in = ds.GetLayer(wetlands_ln)
wetlands_in.SetAttributeFilter("(WETLAND_TY = 'Other')")
#copy of selected and attributed divided roads/carriageways
other_out = ds.CopyLayer(wetlands_in, 'Wetlands_Other')
wetlandTypeList.append('Wetlands_Other')
print wetlandTypeList
ds.GetLayer(wetlands_ln).SetAttributeFilter(None) 
print ("Other extracted from Wetlands")

ds = None






# Script to use proximity analysis and compute mean distance
# from roads.

folder = r'C:\PSU\WetlandsData'
#studyarea_ln = 'studyareaETS_3968'


# Set the cell size for the analysis.
cellsize = 10

shp_ds = ogr.Open(folder)


# Get the extent of the wilderness area.
study_lyr = shp_ds.GetLayerByName(studyarea_ln)
#wild_lyr.SetAttributeFilter("NAME_1_1 = 'Meadow Run'") #study area can go here
#wild_lyr.SetAttributeFilter("WILD_NM = 'Frank Church - RONR'")
envelopes = [row.geometry().GetEnvelope() for row in study_lyr]
coords = list(zip(*envelopes))
minx, maxx = min(coords[0]), max(coords[1])
miny, maxy = min(coords[2]), max(coords[3])

# Select the roads that fall within the wilderness extent.

for wl in wetlandTypeList:
    os.chdir(folder)
    tif_driver = gdal.GetDriverByName('GTiff')
    road_lyr = shp_ds.GetLayerByName(wl)
    road_lyr.SetSpatialFilterRect(minx, miny, maxx, maxy)
    
    # Figure out the output size.
    cols = int((maxx - minx) / cellsize)
    rows = int((maxy - miny) / cellsize)


    # Create an empty raster to hold the rasterized roads.
    road_raster_fn = wl + '.tif'  
    road_ds = tif_driver.Create(road_raster_fn, cols, rows)
    road_ds.SetProjection(road_lyr.GetSpatialRef().ExportToWkt())
    road_ds.SetGeoTransform((minx, cellsize, 0, maxy, 0, -cellsize))

    # Burn the wetlands into the raster.
    gdal.RasterizeLayer(
            road_ds, [1], road_lyr, burn_values=[1],
            callback=gdal.TermProgress)

    # Burn proximity to wetlands into a new raster.
    proximity_fn = wl + '_Prox.tif'
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
            wild_ds, [1], study_lyr, burn_values=[1],
            callback=gdal.TermProgress)

    # Use the temporary wilderness raster to set the proximity one
    # to NoData everywhere that is outside the wilderness area.
    wild_data = wild_ds.ReadAsArray()
    prox_data = prox_ds.ReadAsArray()
    prox_data[wild_data == 0] = -99
    prox_ds.GetRasterBand(1).WriteArray(prox_data)
    prox_ds.GetRasterBand(1).SetNoDataValue(-99)
    prox_ds.FlushCache()

    # Compute statistics and calculate the mean distance to wetlands,
    # which is just the mean value of the proximity raster.
    stats = prox_ds.GetRasterBand(1).ComputeStatistics(
            False, gdal.TermProgress)
    print('Mean distance from ' + wl + ' wetlands is', stats[2])


  #RECLASSIFICATION   
    
    print ("Reclassifying " + wl)
    os.chdir(r'C:\PSU\WetlandsData')
    output_wl_ds = wl + '_Prox_RC.tif'

    in_ds = gdal.Open(proximity_fn)
    in_band = in_ds.GetRasterBand(1)

    list_data = in_band.ReadAsArray()

   
    list_des = list_data.copy()
    
#RECLASSIFICATION VALUES
#Lake = 100, 10, 0
#Pond = 0, 5, 0
#Freshwater Emergent Wetland = 0, 5, 0
#Freshwater Forested/Shrub Wetland = 0, 5, 0
#Riverine = 40, 5, 0
#Other  = = 10, 5, 0
    
    Wetlands_Lake_List = [100,10,0]
    Wetlands_FreshwaterEmergent_List = [0,5,0]
    Wetlands_FreshwaterForested_List = [0,5,0]
    Wetlands_Riverine_List = [40,5,0]
    Wetlands_FreshwaterPond_List = [0,5,0]
    Wetlands_Other_List = [10,5,0]
    
    if 'Lake' in wl:        
        print ("Reclassifying " + wl)
        list_des[np.where( list_data < 1 )] = Wetlands_Lake_List[0]
        list_des[np.where((1 <= list_data) & (list_data <= 15)) ] = Wetlands_Lake_List[1]
        list_des[np.where( list_data > 15 )] = Wetlands_Lake_List[2]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_wl_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + wl + " raster successfully reclassified."
    if 'FreshwaterEmergent' in wl:
        print ("Reclassifying " + wl)
        list_des[np.where( list_data < 1 )] = Wetlands_FreshwaterEmergent_List[0]
        list_des[np.where((1 <= list_data) & (list_data <= 15)) ] = Wetlands_FreshwaterEmergent_List[1]
        list_des[np.where( list_data > 15 )] = Wetlands_FreshwaterEmergent_List[2]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_wl_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + wl + " raster successfully reclassified."
    if 'FreshwaterForested' in wl:
        print ("Reclassifying " + wl)
        list_des[np.where( list_data < 1 )] = Wetlands_FreshwaterForested_List[0]
        list_des[np.where((1 <= list_data) & (list_data <= 15)) ] = Wetlands_FreshwaterForested_List[1]
        list_des[np.where( list_data > 15 )] = Wetlands_FreshwaterForested_List[2]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_wl_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + wl + " raster successfully reclassified."
    if 'Riverine' in wl:
        print ("Reclassifying " + wl)
        list_des[np.where( list_data < 1 )] = Wetlands_Riverine_List[0]
        list_des[np.where((1 <= list_data) & (list_data <= 15)) ] = Wetlands_Riverine_List[1]
        list_des[np.where( list_data > 15 )] = Wetlands_Riverine_List[2]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_wl_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + wl + " raster successfully reclassified."
    if 'FreshwaterPond' in wl:
        print ("Reclassifying " + wl)
        list_des[np.where( list_data < 1 )] = Wetlands_FreshwaterPond_List[0]
        list_des[np.where((1 <= list_data) & (list_data <= 15)) ] = Wetlands_FreshwaterPond_List[1]
        list_des[np.where( list_data > 15 )] = Wetlands_FreshwaterPond_List[2]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_wl_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + wl + " raster successfully reclassified."
    if 'Other' in wl:
        print ("Reclassifying " + wl)
        list_des[np.where( list_data < 1 )] = Wetlands_Other_List[0]
        list_des[np.where((1 <= list_data) & (list_data <= 15)) ] = Wetlands_Other_List[1]
        list_des[np.where( list_data > 15 )] = Wetlands_Other_List[2]
        list_des[np.where( list_data == -99 )] = 255
        file2 = tif_driver.Create(output_wl_ds, in_ds.RasterXSize , in_ds.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(list_des)
        proj = in_ds.GetProjection()
        georef = in_ds.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()
        print "....." + wl + " raster successfully reclassified."
    else:
        continue


os.chdir(r'C:\PSU\WetlandsData')
lake_ds = 'Wetlands_Lake_Prox_RC.tif'
pond_ds = 'Wetlands_FreshwaterPond_Prox_RC.tif'
freshemerge_ds = 'Wetlands_FreshwaterEmergent_Prox_RC.tif'
freshforest_ds = 'Wetlands_FreshwaterForested_Prox_RC.tif'
riverine_ds = 'Wetlands_Riverine_Prox_RC.tif'
other_ds = 'Wetlands_Other_Prox_RC.tif'


output_wl_ds = 'WetlandsFinal.tif'

lake_in = gdal.Open(lake_ds)
lake_band = lake_in.GetRasterBand(1)
lake_list = lake_band.ReadAsArray()

pond_in = gdal.Open(pond_ds)
pond_band = pond_in.GetRasterBand(1)
pond_list = pond_band.ReadAsArray()

freshemerge_in = gdal.Open(freshemerge_ds)
freshemerge_band = freshemerge_in.GetRasterBand(1)
freshemerge_list = freshemerge_band.ReadAsArray()

freshforest_in = gdal.Open(freshforest_ds)
freshforest_band = freshforest_in.GetRasterBand(1)
freshforest_list = freshforest_band.ReadAsArray()

riverine_in = gdal.Open(riverine_ds)
riverine_band = riverine_in.GetRasterBand(1)
riverine_list = riverine_band.ReadAsArray()

other_in = gdal.Open(other_ds)
other_band = other_in.GetRasterBand(1)
other_list = other_band.ReadAsArray()


#create maximum numpy arrays. there is a maximum so compare two, compare results, and continue
max1_out = np.maximum(lake_list,pond_list)
max2_out = np.maximum(max1_out, freshemerge_list)
max3_out = np.maximum(max2_out, freshforest_list)
max4_out = np.maximum(max3_out, riverine_list)
max5_out = np.maximum(max4_out, other_list)

print max5_out

# create new file
#merge_create = driver.Create("merge_roads_test.tif", divrd_in.RasterXSize, divrd_in.RasterYSize, 1, divrd_band.DataType)

#bandOut = merge_create.GetRasterBand(1)


file2 = tif_driver.Create(output_wl_ds, lake_in.RasterXSize , lake_in.RasterYSize , 1)
file2.GetRasterBand(1).WriteArray(max5_out)

# spatial ref system
proj = lake_in.GetProjection()
georef = lake_in.GetGeoTransform()
file2.SetProjection(proj)
file2.SetGeoTransform(georef)
file2.FlushCache()

lake_ds = None
pond_ds = None
freshemerge_ds = None
freshforest_ds = None
riverine_ds = None
other_ds = None
wetlands_ds = None
shp_ds = None

print "SCRIPT COMPLETE"