import rasterio
import numpy as np
import matplotlib.pyplot as plt


# Reading the DEM using rasterio
dem = rasterio.open("Forest Segmented/Yokneam.tif")
rows = dem.height
cols = dem.width
dem_data = dem.read(1).astype("float64")
print(rows, cols)
print(dem.crs)
print(dem.bounds)



def find_differnces_in_neightboring_nodes(dem_data, rows, cols):
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

# def find_good_cells(dem_horizontal, dem_vertical, rows, cols):
#     cells = []
#     for i in range(rows - 2):
#         row = []
#         for j in range(cols - 2):
#             if dem_horizontal[i][j] < 2 and dem_vertical[i][j] < 2\
#                     and dem_horizontal[i][j + 1] < 2 and dem_vertical[i + 1][j] < 2:
#                 row.append(255)
#             else:
#                 row.append(0)
#         cells.append(row)
#     return cells
cells = find_differnces_in_neightboring_nodes(dem_data, rows, cols)

# def add_2d_array_elementwise(a, b):
#     for i in range(len(a)):
#         for j in range(len(a[0])):
#             a[i][j] += b[i][j]
#     return a

def heat_map(cells):
    plt.imshow(cells)
    plt.show()


# Creating empty list to store arrays of values
heat_map(cells)

# arr = list()

# Loop through every cell of the raster
# count = 0
# row = 0
# sum = 0
# while row < rows:
#     col = 0
#     while col < cols:
#         cell = list()
#         cell.append(count)
#         # Get coordinates of current cell
#         cell.append(dem.xy(row, col))
#         # Get elevation of current cell
#         cell.append(dem_data[row, col])
#         # Append helper list to overall list
#         arr.append(cell)
#         col += 1
#         count += 1
#     row += 1
#
# print(arr)