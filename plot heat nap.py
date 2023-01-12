import matplotlib.pyplot as plt
import numpy as np
import rasterio

dem = rasterio.open("DTM/Yokneam.tif")
rows = dem.height
cols = dem.width
dem_data = dem.read(1).astype("float64")


def find_differnces_in_neightboring_nodes(dem_data, rows, cols):
    dem_horizontal = []
    dem_vertical = []
    for i in range(rows - 1):
        row_horizontal = []
        row_vertical = []
        for j in range(cols - 1):
            row_horizontal.append(abs(dem_data[i + 1][j] - dem_data[i][j]))
            row_vertical.append(abs(dem_data[i][j + 1] - dem_data[i][j]))
        dem_horizontal.append(row_horizontal)
        dem_vertical.append(row_vertical)
    return dem_horizontal, dem_vertical


dem_horizontal, dem_vertical = find_differnces_in_neightboring_nodes(dem_data, rows, cols)


def max_2d_array_elementwise(a, b):
    for i in range(len(a)):
        for j in range(len(a[0])):
            a[i][j] = max(a[i][j], b[i][j])
    return a


data_for_plot = max_2d_array_elementwise(dem_horizontal, dem_vertical)
color_map = {0: np.array([0, 255, 0]),  # green
             2: np.array([255, 211, 67]),  # Yellow
             1: np.array([0, 255, 0]),
             3: np.array([255, 0, 0]),
             4: np.array([255, 0, 0]), 5: np.array([255, 0, 0])
    , 6: np.array([255, 0, 0]), 7: np.array([255, 0, 0]), 8: np.array([255, 0, 0]), 9: np.array([255, 0, 0])}  # blue
for i in range(0, rows - 1):
    for j in range(0, cols - 1):
        if dem_horizontal[i][j] > 4:
            data_for_plot[i][j] = np.array([255, 0, 0])
        else:
            data_for_plot[i][j] = color_map[data_for_plot[i][j]]
plt.imshow(data_for_plot, cmap='hot', interpolation='nearest')
plt.show()
