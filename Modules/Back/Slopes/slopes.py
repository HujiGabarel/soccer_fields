import sys
import numpy as np
import rasterio
from typing import Tuple
import matplotlib.pyplot as plt
import math
import tifffile

from settings import DTM_FILE_PATH
PURPLE = (255, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ACCEPTED_SLOPE_COLOR = 255
QUESTIONABLE_SLOPE_COLOR = 255
UNACCEPTED_SLOPE_COLOR = 0


# the file is in format utm36
def get_partial_dtm_from_total_dtm(coordinates: Tuple[int, int, int, str], km_radius: float, meters_per_pixel: float = 10) -> \
        Tuple[np.ndarray, int, int]:
    size = round(km_radius * 1000 / meters_per_pixel)
    # dem = rasterio.open(DTM_FILE_PATH)  # turn .tiff file to dem format, each pixel is a height
    dem = tifffile.imread(DTM_FILE_PATH)
    with tifffile.TiffFile(DTM_FILE_PATH) as tiff:
        # Read the TIFF tags to get spatial information
        tags = tiff.pages[0].tags
        x_origin = tags['ModelTiepointTag'].value[3]
        y_origin = tags['ModelTiepointTag'].value[4]
    # Calculate the bounds
    # if check_coordinates_area_are_in_dtm(coordinates, size, dem):
    #     print("coordinates are in range")
    # else:
    #     print("coordinates are not in range")
    #     raise Exception("coordinates are not in range")
    # calculating the center for partial_dtm
    # col_center = round((coordinates[0] - dem.bounds.left) / meters_per_pixel)
    # row_center = -round((coordinates[1] - dem.bounds.top) / meters_per_pixel)

    col_center = round((coordinates[0] - x_origin) / meters_per_pixel)
    row_center = -round((coordinates[1] - y_origin) / meters_per_pixel)
    # window = rasterio.windows.Window.from_slices((row_center - size, row_center + size + 1),
    #                                              (col_center - size, col_center + size + 1))

    # window = tifffile.imread(DTM_FILE_PATH)
    partial_dtm = dem[row_center - size:row_center + size + 1, col_center - size:col_center + size + 1]

    # partial_dtm = dem.read(1, window=window).astype("int")  # convert height to int instead of float
    new_rows = partial_dtm.shape[0]
    new_cols = partial_dtm.shape[1]

    return partial_dtm, new_rows, new_cols


def check_coordinates_area_are_in_dtm(coordinates: Tuple[int, int, int, str], size: float,
                                      dem: rasterio.DatasetReader) -> bool:
    return ((dem.bounds.left < (coordinates[0] + size) < dem.bounds.right) and
            (dem.bounds.left < (coordinates[0] - size) < dem.bounds.right) and
            (dem.bounds.bottom < (coordinates[1] + size) < dem.bounds.top) and
            (dem.bounds.bottom < (coordinates[1] - size) < dem.bounds.top)
            )


# TODO might have generalization problems, 255 and 0


def get_slopes_mask(coordinates, km_radius, total_mask):
    partial_dtm, new_rows, new_cols = get_partial_dtm_from_total_dtm(coordinates, km_radius)
    slopes_mask = get_max_slopes(partial_dtm, new_rows, new_cols)
    return np.array(convert_slopes_to_black_and_white(slopes_mask, new_rows, new_cols))


# TODO: for loop should be numpy, maybe whole function is irrelevant
def get_max_slopes(dem_data, rows, cols):
    """
    This function returns the maximum height differences in the DEM
    :param dem_data: DEM data as a numpy 2D array
    :param rows: number of rows in the DEM
    :param cols: number of columns in the DEM
    :return: a 2D array of maximum height differences,
            one row and one col less than the DEM, because we are working between 4 points
    """
    cells = []
    for i in range(rows - 1):
        row = []
        for j in range(cols - 1):
            row.append(min(2, max(abs(dem_data[i][j + 1] - dem_data[i][j]),
                                  abs(dem_data[i + 1][j + 1] - dem_data[i + 1][j]),
                                  abs(dem_data[i + 1][j] - dem_data[i][j]),
                                  abs(dem_data[i + 1][j + 1] - dem_data[i][j + 1]))))
        cells.append(row)
    return cells


def plot_heat_map(data_in_black_and_white):
    plt.imshow(data_in_black_and_white, interpolation='nearest')
    plt.show()


# TODO: for loop should be numpy, combine with previous using more than 2 instead of casting to 2
def convert_slopes_to_black_and_white(height_differences, rows, cols):
    data_in_black_and_white = height_differences
    color_map = {0: ACCEPTED_SLOPE_COLOR,
                 1: QUESTIONABLE_SLOPE_COLOR,
                 2: UNACCEPTED_SLOPE_COLOR}
    for i in range(0, rows - 1):
        for j in range(0, cols - 1):
            data_in_black_and_white[i][j] = color_map[data_in_black_and_white[i][j]]
    return data_in_black_and_white
    # interpolation makes it so its strictly black and white


if __name__ == '__main__':
    """
    This is the main function, it reads the DEM and plots a heat map of the maximum height differences
    Very specific, only works on DTM_data with 10 meter resolution, with 1 meter accuracy
    To fix, need to rethink the process for this class (with a whiteboard)
    """
    #  The maximum angle for landing a Yaswor is 8 deg, therefore:
    # maximal height differences = tan(8) * resolution
    # in 10 meter resolution the maximum height differences is about 1.5 meters
    resolution = 10
    max_angle = 8
    maximal_slope = resolution * math.tan(max_angle * math.pi / 180)
    dem = rasterio.open(DTM_FILE_PATH)
    rows = dem.height
    cols = dem.width
    dem_data = dem.read(1).astype("float64")
    print("rows: " + str(rows), "cols: " + str(cols))
    print(dem.crs)
    print(dem.bounds)
    plot_heat_map(dem_data)
