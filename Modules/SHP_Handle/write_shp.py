import numpy as np
import shapefile
import cv2
# from skimage import io
# import numpy as np
# from skimage.measure import label
# from skimage.measure import regionprops
# from shapely.geometry import Polygon
# from skimage.measure import regionprops
# from shapely.geometry import Polygon
# import geopandas as gpd
# def image_file_to_shp_file(image_name):
#     img = io.imread(image_name, as_gray=True)
#
#     threshold = 0.5  # adjust this threshold as needed
#     mask = np.where(img > threshold, 1, 0)
#
#     labeled = label(mask)
#
#     polygons = []
#     for props in regionprops(labeled):
#         polygons.append(Polygon(props.coords[:, ::-1]).buffer(0))
#         print(polygons)
#
#     merged_polygon = gpd.GeoSeries(polygons).unary_union
#     gdf = gpd.GeoDataFrame(geometry=[merged_polygon])
#     gdf.to_file("output.shp")
def convert_row_col2coordinates(row, col, x_min, y_min, pixel_size):
    """
    convert row and col to x and y
    :param row: row
    :param col: col
    :param x_min: x_min
    :param y_min: y_min
    :param pixel_size: pixel_size
    :return: x,y
    """
    pass


def convert_mask2polygons(mask):

    pass

def convert_mask2shp(mask: np.ndarray, directory_path: str):
    """
    convert the mask to shapefile and save it in the directory_path
    :param mask:
    :param directory_path:
    :return: none
    """
    list_of_polygons = convert_mask2polygons(mask)
    # Create a polygon shapefile writer
    return None

