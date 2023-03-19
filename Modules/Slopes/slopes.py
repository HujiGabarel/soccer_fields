import rasterio
import matplotlib.pyplot as plt

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (255, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ACCEPTED_SLOPE_COLOR = WHITE
QUESTIONABLE_SLOPE_COLOR = WHITE
UNACCEPTED_SLOPE_COLOR = BLACK
DTM_FILE_PATH = "../../DTM Data/some.tif"


def get_max_height_differences(dem_data, rows, cols):
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


def plot_heat_map(height_differences):
    """
    This function plots a heat map of the height differences
    :param height_differences: height differences as a 2D array
    :return: None, but plots a heat map for 0 (good), 1 (medium) and 2 (bad)
    """
    data_for_plot = height_differences
    color_map = {0: ACCEPTED_SLOPE_COLOR,
                 1: QUESTIONABLE_SLOPE_COLOR,
                 2: UNACCEPTED_SLOPE_COLOR}
    for i in range(0, rows - 1):
        for j in range(0, cols - 1):
            data_for_plot[i][j] = color_map[data_for_plot[i][j]]
    # interpolation makes it so its strictly black and white
    plt.imshow(data_for_plot, interpolation='nearest')
    plt.show()


if __name__ == '__main__':
    """
    This is the main function, it reads the DEM and plots a heat map of the maximum height differences
    Very specific, only works on DTM_data with 10 meter resolution, with 1 meter accuracy
    To fix, need to rethink the process for this class (with a whiteboard)
    """
    dem = rasterio.open(DTM_FILE_PATH)
    rows = dem.height
    cols = dem.width
    dem_data = dem.read(1).astype("float64")
    # print general information about the DEM
    print("rows: " + str(rows), "cols: " + str(cols))
    print(dem.crs)
    print(dem.bounds)
    max_height_differences = get_max_height_differences(dem_data, rows, cols)
    plot_heat_map(max_height_differences)
