import matplotlib.pyplot as plt
import numpy as np
import os
import json
import datetime
import image_downloading
import cv2
import utm
from Modules.Slopes.slopes import get_max_slope, plot_heat_map
import rasterio

#TODO: decide about length
def get_image_from_utm(coordinates):
    """

    Args:
        coordinates (_type_): _description_
    """

    with open("preferences.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    coordinates = utm.from_latlon(coordinates[0],coordinates[1])

    lat,long = image_downloading.convert_to_lat_long(coordinates)
    img = image_downloading.download_image(lat,long,prefs["zoom"],prefs['url'] ,prefs['tile_size'],length=1.5)
    return img

    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # name = f'images_from_argcis/img_{timestamp}.png'
    # cv2.imwrite(name, img)
    # print(f'Saved as {name}')



    pass


def get_tree_mask_from_image(aerial):
    # using trees module, get the mask of the trees in black white
    pass


def get_partial_dtm_from_total_dtm(coordinates, SIZE, meters_per_pixel=10):
    # find the area in the dtm that is relevant
    # cut around the area in a SIZE*SIZE matrix

    file_path = "../../DTM_data/some.tif"  # path to .tiff file
    dem = rasterio.open(file_path)  # turn .tiff file to dem format, each pixel is a height
    rows = dem.height  # number of rows
    cols = dem.width  # number of columns
    dem_data = dem.read(1).astype("int")  # convert height to int instead of float

    ### assuming that the coordinates[0] is cols (east / west) and coordinates[1] is rows (north / south)

    # calculating the center for partial_dtm
    row_center = round((coordinates[1] - dem.bounds.bottom) / meters_per_pixel)
    col_center = round((coordinates[0] - dem.bounds.left) / meters_per_pixel)

    sub_matrix = dem_data[row_center - SIZE: row_center + SIZE, col_center - SIZE: col_center + SIZE]
    new_rows = sub_matrix.shape[0]
    new_cols = sub_matrix.shape[1]
    partial_max_slopes = get_max_slope(sub_matrix, new_rows, new_cols)

    return partial_max_slopes, new_rows, new_cols


def get_total_mask_from_masks(tree_mask, heights_mask):
    # return tree_mask * heights_mask
    tree_mask_np=np.array(tree_mask)
    heights_mask_np=np.array(heights_mask)
    return np.multiply(tree_mask_np,heights_mask_np)


"""def get_slopes_mask_from_dtm(dtm):
    # get heights from the dtm
    # get slopes from the heights
    # get mask from the slopes
    # return mask
    #TODO: SIZE of the image is constant?
    #retuen get_max_slope(dtm, )
    pass"""


def get_viable_landing_in_radius(coordinates, km_radius = 1):
    aerial = get_image_from_utm(coordinates, km_radius)
    tree_mask = get_tree_mask_from_image(aerial)
    dtm = get_partial_dtm_from_total_dtm(coordinates, km_radius)
    slopes_mask = get_slopes_mask_from_dtm(dtm)
    total_mask = get_total_mask_from_masks(tree_mask, slopes_mask)
    plt.imshow(total_mask)
    pass


def main():
    """coordinates = (0, 0)
    get_viable_landing_in_radius(coordinates)"""
    coordinates = (685825.0, 3625765.0)
    radius_in_km=3
    meters_per_pixel = 10
    SIZE = round(radius_in_km*1000/meters_per_pixel)
    partial_max_height_diff, new_rows, new_cols = get_partial_dtm_from_total_dtm(coordinates, SIZE, meters_per_pixel)
    plot_heat_map(partial_max_height_diff, new_rows, new_cols)


if __name__ == '__main__':
    main()

