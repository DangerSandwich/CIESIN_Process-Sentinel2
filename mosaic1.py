import numpy as np
import os
import gdal
import subprocess

def merge_eachzone(list, band):
#make a string contains all the input
    output = output_dir + list[0][:2] + band + "_mosaic.tif"
    #cmd = "gdal_merge.py -n 0 -a_nodata 0 -of GTiff -o $OutputDir/"$Dataset"_avgIRI_"$Month1""$Year1"_"$Month2""$Year2"'_mosaic.tif' $tiflist "
    cmd = ['gdal_merge.py', '-o', output]
    for input in list:
        input = input_dir + band + '/' + input
        cmd.append(input)
    if band == 'NDVI':
        print cmd
    subprocess.call(cmd)

def classify_zone(target):
    dict = {}
    tif_names = []
    for (dirpath, dirnames, filenames) in os.walk(target):
        tif_names.extend(filenames)
    for tif in tif_names:
        zone = tif[:2]
        if zone not in dict:
            dict[zone] = []
            dict[zone].append(tif)
        else:
            dict[zone].append(tif)
    return dict


if __name__ == '__main__':
#find each zone file in each band folder
    input_dir = "/data2/sentinel2/analysis_test/pickup/"
    output_dir = "/data2/sentinel2/analysis_test/mosaic/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    one_bandfolder = next(os.walk(input_dir))[1]
#mosaic by zone in each band
    for band in one_bandfolder:
        zone_dic = classify_zone(input_dir + band)
        for k in zone_dic:
            merge_eachzone(zone_dic[k], band)
#mosaic all the zone
