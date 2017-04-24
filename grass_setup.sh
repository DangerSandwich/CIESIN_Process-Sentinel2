#Starting GRASS Environment
#some settings:
TMPDIR=/tmp
ClipDir=/data2/gadm2/countries
clipfile2=TZ_100m_LAEA
clipfile=TZ_100m_LAEA.tif
mapsetName=test
# path to GRASS binaries and libraries:
export GISBASE=/usr/lib/grass64

#Create temporary mapset with WIND parameter
mkdir /data3/grassdata/lambert/$mapsetName
cp /data3/grassdata/lambert/PERMANENT/WIND /data3/grassdata/lambert/$mapsetName

# generate GRASS settings file:
# the file contains the GRASS variables which define the LOCATION etc.
echo "GISDBASE: /data3/grassdata
LOCATION_NAME: lambert
MAPSET: $mapsetName
" > $TMPDIR/.grassrc6_modis123

# path to GRASS settings file:
export GISRC=$TMPDIR/.grassrc6_modis123

# first our GRASS, then the rest
export PATH=$GISBASE/bin:$GISBASE/scripts:$PATH
#first have our private libraries:
export LD_LIBRARY_PATH=$GISBASE/lib:$LD_LIBRARY_PATH

# use process ID (PID) as lock file number:
export GIS_LOCK=123

# this should print the GRASS version used:
g.version
g.gisenv -n


r.in.gdal input=$ClipDir/$clipfile output=$clipfile2
r.mask -o input=$clipfile2@"$mapsetName"
g.region rast=$clipfile2@"$mapsetName"
