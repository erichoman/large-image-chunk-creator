import os
import sys
import rasterio
from rasterio.windows import Window
import numpy as np

def convert_coordinates(value, minimum, maximum):
    range_diff = maximum - minimum
    return (value - minimum) % range_diff + minimum

# get the input filename and output folder from the command-line arguments
input_filename = sys.argv[1]
output_folder = sys.argv[2]

# get the rasterio dataset
dataset = rasterio.open(input_filename)

# define the size of chunks
width, height = 1024, 1024

# get the number of chunks
rows = dataset.width // width
cols = dataset.height // height

# get the pixel resolution
resolution = 200  # meters/pixel

# make sure the output folder exists
os.makedirs(output_folder, exist_ok=True)

minimum_lat = -90.0
maximum_lat = 90.0
minimum_lon = -180.0
maximum_lon = 180.0

for i in range(rows):
    for j in range(cols):
        # define the window of data to read
        window = Window(i*width, j*height, width, height)
        
        # get the transformation for this window
        transform = rasterio.windows.transform(window, dataset.transform)

        # get the pixel position of the top left corner of the window
        px, py = transform * (0, 0)

        # calculate the longitude and latitude using your convert_coordinates function
        lon = convert_coordinates(px, minimum_lon, maximum_lon)
        lat = convert_coordinates(py, minimum_lat, maximum_lat)

        # define the output filename
        output_filename = f"{output_folder}/long_{lon:.6f}_lat_{lat:.6f}.tif"

        # check if this file already exists
        if os.path.exists(output_filename):
            print(f"Skipping {output_filename}, already exists")
            continue

        # read the data in the window
        data = dataset.read(1, window=window)

        # normalize data
        data_min = np.min(data)
        data_max = np.max(data)
        data = (data - data_min) / (data_max - data_min) * 65535  # 65535 for 16 bit
        data = data.astype(np.uint16)
        
        # write the output file
        with rasterio.open(
            output_filename,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=data.dtype,
            crs=dataset.crs,
            transform=transform,
        ) as dst:
            dst.write(data, 1)

print('Completed processing')
