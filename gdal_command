# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 15:36:08 2018

@author: tom
"""

#raster preparation
#this is done using GDAL on the command line (osgeo shell) until I 
#integrate it using subprocess or os?

#all landcover tifs should be in a single location

cd C:\PSU\ScriptRaster

#reproject rasters in folder so that they all match. processes will
#not work if they are not the same
#https://medium.com/planet-stories/a-gentle-introduction-to-gdal-part-2-map-projections-gdalwarp-e05173bd710a
gdalwarp -t_srs EPSG:3968 -wo SOURCE_EXTRA=1000 -co COMPRESS=LZW N16_36.tif N16_36_rp2.tif


#get a list of the tifs in the folder and save them to a txt file for processing
dir /b /s *.tif >tif_list.txt
#link
#https://gis.stackexchange.com/questions/230553/merging-all-tiles-from-one-directory-using-gdal/230588

#save as a vrt (virtual file)
gdalbuildvrt lc.vrt -input_file_list tif_list.txt

#save vrt as a tif
gdal_translate lc.vrt lc.tif

gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3968 -wo SOURCE_EXTRA=1000 -co COMPRESS=LZW reclassifed_lc.tif reclass_lc_rp.tif
