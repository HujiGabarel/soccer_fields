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



