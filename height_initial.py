import rasterio

# Reading the DEM using rasterio
dem = rasterio.open("Forest Segmented/Yokneam.tif")
rows = dem.height
cols = dem.width
dem_data = dem.read(1).astype("float64")
print(rows, cols)
print(dem.crs)
print(dem.bounds)

# Creating empty list to store arrays of values
arr = list()

# Loop through every cell of the raster
count = 0
row = 0
sum = 0
while row < rows:
    col = 0
    while col < cols:
        cell = list()
        cell.append(count)
        # Get coordinates of current cell
        cell.append(dem.xy(row, col))
        # Get elevation of current cell
        cell.append(dem_data[row, col])
        # Append helper list to overall list
        arr.append(cell)
        col += 1
        count += 1
    row += 1

print(arr)