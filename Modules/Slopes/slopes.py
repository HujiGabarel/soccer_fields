import rasterio
import matplotlib.pyplot as plt
import utm
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (255, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ACCEPTED_SLOPE_COLOR = WHITE
QUESTIONABLE_SLOPE_COLOR = WHITE
UNACCEPTED_SLOPE_COLOR = BLACK


# the file is in format utm36
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


def utm_to_WGS84(easting, northing, zone_number=36, zone_letter='u'):
    """
    :param easting:
    :param northing:
    :param zone_number:
    :param zone_letter:
    :return: (latitude, longitude) WGS84 format, Google Earth format
    """
    return utm.to_latlon(easting, northing, zone_number, zone_letter)


def WGS84_to_utm(latitude, longitude):
    """
    :param latitude:
    :param longitude:
    :return: (easting, northing, zone_number, zone_letter) utm format, our dtm format
    """
    return utm.from_latlon(latitude, longitude)


if __name__ == '__main__':
    """
    This is the main function, it reads the DEM and plots a heat map of the maximum height differences
    Very specific, only works on DTM_data with 10 meter resolution, with 1 meter accuracy
    To fix, need to rethink the process for this class (with a whiteboard)
    """
    #  The maximum angle for landing a Yaswor is 8 deg, therefore:
    # maximal height differences = tan(8) * resolution
    # in 10 meter resolution the maximum height differences is about 1.5 meters
    DTM_FILE_PATH = "../../DTM_data/top.tif"
    resolution = 10
    maximal_slope = resolution * math.tan(8 * math.pi / 180)
    dem = rasterio.open(DTM_FILE_PATH)
    rows = dem.height
    cols = dem.width
    dem_data = dem.read(1).astype("float64")
    # print general information about the DEM
    print("rows: " + str(rows), "cols: " + str(cols))
    print(dem.crs)
    print(dem.bounds)
    # max_slopes = get_max_slopes(dem_data, rows, cols)
    # data_in_black_and_white = convert_slopes_to_black_and_white(max_slopes, rows, cols)
    # max_slopes_in_binary = plot_heat_map(data_in_black_and_white)
