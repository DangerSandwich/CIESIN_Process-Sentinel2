import gdal
import numpy as np
import os
import subprocess

#calculate the mndwi (modified normalized water index by Xu 2006) and return the index
def calculateMNDWI(tile):

    count = 0
    #Pick up the files of B03 and B11
    band03_dir = resample_dir + tile + '/' + 'B03/'
    band11_dir = resample_dir + tile + '/' + 'B11/'
    band03_list = []
    band11_list = []
    for (dirpath, dirnames, filenames) in os.walk(band03_dir):
        band03_list.extend(filenames)
    for (dirpath, dirnames, filenames) in os.walk(band11_dir):
        band11_list.extend(filenames)
    #pick up the B03 and B11 and flatten the matrix to array
    band03_matrix = []
    band11_matrix = []
    #sort two file list
    band03_list.sort()
    band11_list.sort()
    for b03 in band03_list:
        # file_dir = resample_dir + zone + '/' + tile + '/' + band
        file_dir = band03_dir + b03
        raster = gdal.Open(file_dir)
        banddataraster = raster.GetRasterBand(1)
        dataraster = banddataraster.ReadAsArray().astype(np.float)
        shape = dataraster.shape
        band03_matrix.append(dataraster.flatten())

    for b03 in band11_list:
        # file_dir = resample_dir + zone + '/' + tile + '/' + band
        file_dir = band11_dir + b11
        raster = gdal.Open(file_dir)
        banddataraster = raster.GetRasterBand(1)
        dataraster = banddataraster.ReadAsArray().astype(np.float)
        band11_matrix.append(dataraster.flatten())
    # np.savetxt('test.txt', np.array(band03_list), delimiter=',')
    # np.savetxt('test.txt', np.array(band11_list), delimiter = ',')
    #transform list back to np-array(matrix)
    geoTransform = raster.GetGeoTransform()
    geoProjection = raster.GetProjection()
    shape = dataraster.shape
    band03_matrix = np.array(band03_matrix)
    band11_matrix = np.array(band11_matrix)
    diff = band03_matrix - band11_matrix
    summ = band03_matrix + band11_matrix
    mndwi = diff / summ
    mndwi[np.where(summ == 0)] = -1
    mndwi = np.where(mndwi == 1, -1, ndvi)
    mndwi_pickup = np.amax(mndwi, axis = 0)
    index_max = np.argmax(mndwi, axis = 0)
    ndvi_matrix = mndwi_pickup.reshape(shape)
    np.savetxt("test.txt", mndwi_matrix, delimiter = ',')
    #call the create_tiff function to transform the output into a tif
    tif_dir = output_dir + 'MNDWI/'
    tif_name = tif_dir + tile + '_MNDWI.tif'
    if os.path.isfile(tif_name):
        return index_max
    if not os.path.exists(tif_dir):
        os.makedirs(tif_dir)
    create_tif(tif_name, mndwi_matrix, geoTransform, geoProjection)
    return index_max

#define the function to create the tif file
def create_tif(filename, matrix, geoTransform, geoProjection):
''' Create an output file of the same size as the inputted
image, but with only 1 output image band.'''

    driver = gdal.GetDriverByName( "GTiff" )
    cols = matrix.shape[1]
    rows = matrix.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(filename, cols, rows, 1, gdal.GDT_Float32)
    outband = outRaster.GetRasterBand(1)
# Define the spatial information for the new image.
    outRaster.SetGeoTransform(geoTransform)
    outband.WriteArray(matrix)
    outRaster.SetProjection(geoProjection)
    outband.FlushCache()
    return

#define the function to pickup value of different band
def pick_up(index, band, tile):
    tif_dir = output_dir + band + '/'
    tif_name = tif_dir + tile + '_' + band + '.tif'
    if os.path.isfile(tif_name):
        return
    band_dir = resample_dir + tile + '/' + band + '/'
    filenames = []
    for (dirpath, dirnames, filename) in os.walk(band_dir):
        filenames.extend(filename)
    band_matrix = []
    filenames.sort()
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
    band_out = band_matrix[row, col]

    band_matrix = band_out.reshape(shape)
    if not os.path.exists(tif_dir):
        os.makedirs(tif_dir)

    geoTransform = raster.GetGeoTransform()
    geoProjection = raster.GetProjection()
    create_tif(tif_name, band_matrix, geoTransform, geoProjection)


if __name__ == '__main__':

    #resample_dir = "/data2/sentinel2/analysis/tanzania/raws_100m/"
    resample_dir = "/data3/rstudio/sentinel2/raws_100m/"
    output_dir="/data2/sentinel2/analysis_test/pickup/"
    tile_list_test = next(os.walk(resample_dir))[1]
    bands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B11', 'B12', 'B8A']
    count = 0
    for tile in tile_list_test:
        print "calculate the MNDWI of tile", tile
        index = calculateNDVI(tile)
        for band in bands:
            print "pick up", band
            pick_up(index, band, tile)
        count += 1

    print count, "tile in total"
