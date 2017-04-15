import gdal
import numpy as np
import os
import subprocess

#calculate the ndvi and return the index
def calculateNDVI(tile):
    count = 0
    #Pick up the files of B04 and B08
    band4_dir = resample_dir + tile + '/' + 'B04/'
    band8_dir = resample_dir + tile + '/' + 'B08/'
    band4_list = []
    band8_list = []
    for (dirpath, dirnames, filenames) in os.walk(band4_dir):
        band4_list.extend(filenames)
    for (dirpath, dirnames, filenames) in os.walk(band8_dir):
        band8_list.extend(filenames)
    #pick up the B04 and B08 and flatten the matrix to array
    band4_matrix = []
    band8_matrix = []
    for b4 in band4_list:
        # file_dir = resample_dir + zone + '/' + tile + '/' + band
        file_dir = band4_dir + b4
        raster = gdal.Open(file_dir)
        banddataraster = raster.GetRasterBand(1)
        dataraster = banddataraster.ReadAsArray().astype(np.float)
        shape = dataraster.shape
        band4_matrix.append(dataraster.flatten())

    for b8 in band8_list:
        # file_dir = resample_dir + zone + '/' + tile + '/' + band
        file_dir = band8_dir + b8
        raster = gdal.Open(file_dir)
        banddataraster = raster.GetRasterBand(1)
        dataraster = banddataraster.ReadAsArray().astype(np.float)
        band8_matrix.append(dataraster.flatten())
    #transform list back to np-array(matrix)
    geoTransform = raster.GetGeoTransform()
    geoProjection = raster.GetProjection()
    shape = dataraster.shape
    band4_matrix = np.array(band4_matrix)
    band8_matrix = np.array(band8_matrix)
    diff = band8_matrix - band4_matrix
    summ = band4_matrix + band8_matrix
    ndvi = diff / summ
    ndvi[np.where(summ == 0)] = -1
    ndvi = np.where(ndvi == 1, -1, ndvi)
    ndvi_pickup = np.amax(ndvi, axis=0)
    index_max = np.argmax(ndvi, axis = 0)
    print ndvi_pickup.shape
    print shape
    ndvi_matrix = ndvi_pickup.reshape(shape)
    #call the create_tiff function to transform the output into a tif
    tif_dir = output_dir + 'NDVI/'
    tif_name = tif_dir + tile + '_NDVI.tif'
    if not os.path.exists(tif_dir):
        os.makedirs(tif_dir)
    create_tif(tif_name, ndvi_matrix, geoTransform, geoProjection)
    return index_max
        # return index_max

#define the function to create the tif file
def create_tif(filename, matrix, geoTransform, geoProjection):
    driver = gdal.GetDriverByName( "GTiff" )
    # Create an output file of the same size as the inputted
    # image, but with only 1 output image band.

    cols = matrix.shape[1]
    rows = matrix.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(filename, cols, rows, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
    outRaster.SetGeoTransform(geoTransform)
    outband.WriteArray(matrix)
    outRaster.SetProjection(geoProjection)
    outband.FlushCache()
    # Define the spatial information for the new image.

    return

#define the function to pickup value of different band
def pick_up(index, band, tile):

    band_dir = resample_dir + tile + '/' + band + '/'
    filenames = []
    for (dirpath, dirnames, filename) in os.walk(band_dir):
        filenames.extend(filename)
    band_matrix = []
    for band_file in filenames:
        raster = gdal.Open(band_dir + band_file)
        banddataraster = raster.GetRasterBand(1)
        dataraster = banddataraster.ReadAsArray().astype(np.float)
        band_matrix.append(dataraster.flatten())
    band_matrix = np.array(band_matrix)
    #get the row index of the max value
    shape = dataraster.shape
    ncol = shape[0] * shape[1]
    col = np.indices((1, ncol))[1]
    row = index
    print row.shape
    print col.shape
    band_out = band_matrix[row, col]
    tif_dir = output_dir + band + '/'
    tif_name = tif_dir + tile + '_' + band + '.tif'
    band_matrix = band_out.reshape(shape)
    if not os.path.exists(tif_dir):
        os.makedirs(tif_dir)

    geoTransform = raster.GetGeoTransform()
    geoProjection = raster.GetProjection()
    create_tif(tif_name, band_matrix, geoTransform, geoProjection)


if __name__ == '__main__':

    resample_dir = "/data2/sentinel2/analysis/tanzania/raws_100m/"
    output_dir="/data2/sentinel2/analysis_python/pickup/"
    tile_list_test = next(os.walk(resample_dir))[1]
    bands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B11', 'B12', 'B8A']
    count = 0
    for tile in tile_list_test:
        index = calculateNDVI(tile)
        for band in bands:
            pick_up(index, band, tile)
        count += 1

    print count, "tile in total"

