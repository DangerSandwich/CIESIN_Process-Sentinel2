import subprocess
import gdal
import os
#revise the projection of all the mosaic file
input_dir = "/data2/sentinel2/analysis_test/mosaic/"
output_dir  = "/data2/sentinel2/analysis_test/mosaic_repro/"
mapsetname = "test"
mosaic_output = "/data2/sentinel2/analysis_test/output/"
#Starting GRASS Environment
#some settings:
# path to GRASS settings file:

setting = "TMPDIR=/tmp\nexport GISBASE=/usr/lib/grass64\nexport GISRC=$TMPDIR/.grassrc6_modis123\nexport PATH=$GISBASE/bin:$GISBASE/scripts:$PATH\nexport LD_LIBRARY_PATH=$GISBASE/lib:$LD_LIBRARY_PATH\nexport GIS_LOCK=123\n"

# filenames = []
# for (dirpath, dirnames, filenames) in os.walk(input_dir):
#     filenames.extend(filenames)
# for f in filenames:
#     band = f[2:5]
#     inputfile = input_dir + f
#     outband_dir = output_dir + band
#     outputfile = outband_dir + '/' + f[:-4] + '_repro.tif'
#     if not os.path.exists(outband_dir):
#         os.makedirs(outband_dir)
#     projectioncmd = "gdalwarp -overwrite -t_srs '+proj=laea +lat_0=5 +lon_0=20 +x_0=0 +y_0=0 +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs' -multi -wm 5000 "
#     p1 = subprocess.Popen(projectioncmd + inputfile + ' ' + outputfile , shell = True)
#     p1.wait()

#set up the grass
p_setup = subprocess.call("./grass_setup.sh", shell = True)

#get all the zone of every band
bands = next(os.walk(output_dir))[1]
count = 0
for band in bands:
    count += 1
    zonefile = []
    for (dirpath, dirnames, filenames) in os.walk(output_dir + band):
        zonefile.extend(filenames)
    for f in zonefile:
        input_bash = output_dir + band + '/' + f
        readcmd = setting + "r.in.gdal input=" + input_bash + " output=" + f[:-4]
        p_readintograss = subprocess.Popen(readcmd, shell = True)
        p_readintograss.wait()
        setnacmd = setting + "r.null map="+f[:-4]+"@"+mapsetname+" setnull=0"
        p_setnacmd = subprocess.Popen(setnacmd, shell = True)
        p_setnacmd.wait()
    #make the input string
    string = ''
    for f in zonefile:
        string += f[:-4]+ "@" + mapsetname + ','
    string = string[:-1]
    mosaiccmd = setting+"r.patch input="+string+" output="+band
    #mosaiccmd = "r.patch input=NDVI1@test,NDVI2@test,NDVI3@test output=NDVI"
    p_mosaic_zone = subprocess.Popen(mosaiccmd, shell = True)
    p_mosaic_zone.wait()
    #r.out.gdal input=NDVI@test output=/data2/sentinel2/NDVI.tif
    if not os.path.exists(mosaic_output):
        os.makedirs(mosaic_output)
    mosaic_out_cmd = setting + "r.out.gdal input="+band+"@"+ mapsetname+" output="+mosaic_output+band+".tif"
    p_mosaic_out = subprocess.Popen(mosaic_out_cmd, shell = True)
    p_mosaic_out.wait()



# subprocess.call("", shell = True)
