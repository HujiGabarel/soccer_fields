import matplotlib.pyplot as plt
import numpy as np
import os
import json
import datetime
import image_downloading
import cv2
import utm
from Modules.Slopes.slopes import get_max_slopes, plot_heat_map, convert_slopes_to_black_and_white
import rasterio
from Modules.Trees.predict_with_trained_model import predict_image
import cv2


# TODO: decide about length
def get_image_from_utm(coordinates, km_radius):
    """

    Args:
        coordinates (_type_): _description_
    """

    with open("preferences.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    lat, long = image_downloading.convert_to_lat_long(coordinates)
    img = image_downloading.download_image(lat, long, prefs["zoom"], prefs['url'], prefs['tile_size'], length=km_radius)
    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'images_from_argcis/img_{coordinates[0],coordinates[1]}.png'
    cv2.imwrite(name, img)
    print(f'Saved as {name}')
    return name



def get_tree_mask_from_image(aerial, trained_model_path):
    # using trees module, get the mask of the trees in black white
    return predict_image(aerial, trained_model_path)


def cheack_coordinates_area_are_out_of_dtm(coordinates, size, dem):
    return not ((dem.bounds.left < coordinates[0] + size < dem.bounds.right) and
                (dem.bounds.left < coordinates[0] - size < dem.bounds.right) and
                (dem.bounds.bottom < coordinates[1] + size < dem.bounds.top) and
                (dem.bounds.bottom < coordinates[1] - size < dem.bounds.top)
                )


def get_partial_dtm_from_total_dtm(coordinates, km_radius, meters_per_pixel=10):
    # find the area in the dtm that is relevant
    # cut around the area in a SIZE*SIZE matrix
    size = round(km_radius * 1000 / meters_per_pixel)
    dem = rasterio.open(DTM_FILE_PATH)  # turn .tiff file to dem format, each pixel is a height
    rows = dem.height  # number of rows
    cols = dem.width  # number of columns
    dem_data = dem.read(1).astype("int")  # convert height to int instead of float

    ### assuming that the coordinates[0] is cols (east / west) and coordinates[1] is rows (north / south)

    # calculating the center for partial_dtm
    if cheack_coordinates_area_are_out_of_dtm(coordinates, size, dem):
        print("coordinates are out of range")
    row_center = round((coordinates[0] - dem.bounds.left) / meters_per_pixel)
    col_center = round((coordinates[1] - dem.bounds.bottom) / meters_per_pixel)

    partial_dtm = dem_data[row_center - size: row_center + size, col_center - size: col_center + size]
    new_rows = partial_dtm.shape[0]
    new_cols = partial_dtm.shape[1]

    return partial_dtm, new_rows, new_cols


def get_total_mask_from_masks(tree_mask, heights_mask):
    # return tree_mask * heights_mask
    tree_mask_np = np.array(tree_mask)
    heights_mask_np = np.array(heights_mask)
    return np.multiply(tree_mask_np, heights_mask_np)


def get_viable_landing_in_radius(coordinates, km_radius):
    image_name = get_image_from_utm(coordinates, km_radius)
    partial_dtm, new_rows, new_cols = get_partial_dtm_from_total_dtm(coordinates, km_radius)
    slopes_mask = get_max_slopes(partial_dtm, new_rows, new_cols)
    slopes_mask_in_black_and_white = convert_slopes_to_black_and_white(slopes_mask, new_rows, new_cols)
    plot_heat_map(slopes_mask_in_black_and_white)
    # this work with image name only when image is in Main dir, else need full path
    tree_mask = get_tree_mask_from_image(image_name, trained_model_path)
    # total_mask = get_total_mask_from_masks(tree_mask, slopes_mask_in_black_and_white)
    # plt.imshow(total_mask)
    pass


if __name__ == '__main__':
    # BoundingBox(left=692125.0, bottom=3614785.0, right=705335.0, top=3623875.0)

    coordinates = (695125.0, 3618785.0, 36, "u")
    km_radius = 0.5
    DTM_FILE_PATH = "../../DTM_data/Yokneam.tif"
    trained_model_path = "../../Models/our_models/official_masks_10%.joblib"  # The trained model
    get_viable_landing_in_radius(coordinates, km_radius)
