import gdal
import numpy as np
import os
import subprocess

raw_dir="/data1/sentinel2/raws/tanzania/2016s1/"
output_dir="/data2/sentinel2/analysis_python/resample/"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
first_folder = next(os.walk(raw_dir))[1]

# resample the graph to 100 meter
def resample(name):
    #get the location of granule dir
    granule = raw_dir + name + "/GRANULE/"
    #get all the dir under granule
    last_level = next(os.walk(granule))[1]
    for index in last_level:
        img_dir = granule + index + '/IMG_DATA/'
        file_names = []
        for (dirpath, dirnames, filenames) in os.walk(img_dir):
            file_names.extend(filenames)
        for jptwo in file_names:
            #get the final input dir and output dir
            jptwo_dir = img_dir + jptwo
            #extract the zone and tile name
            zone = jptwo[-13: -11]
            tile = jptwo[-13: -8]
            band = jptwo[-7: -4]
            write_dir = output_dir + tile + '/' + band + '/'
            write_file = write_dir + jptwo[:-4] + '_resample.tif'
            #if the jpeg has already been resample, continue
            if os.path.isfile(write_file):
                continue

            #create a dir if the output path don't exists
            if not os.path.exists(write_dir):
                os.makedirs(write_dir)

            print write_dir
            #call bash to excute the resample
            cmd = "gdalwarp -r average -tr 100 100 -overwrite -srcnodata 0 -multi -wm 5000 "
            process = subprocess.Popen(cmd+jptwo_dir+' '+write_file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stderr = ''.join(process.stderr.readlines())
            #if there is a error, print it
            if len(stderr) > 0:
                raise IOError(stderr)

for data in first_folder:
    resample(data)
