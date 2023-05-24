import sys
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import numpy as np
import json
import cv2
import rasterio as rio
from rasterio import plot
import time
from Modules.GUI.settings import *
from Modules.Main.Processing_runtimes import data_analyse
from Modules.Main.utils import *
from Modules.SHP_Handle.read_shp import get_mask_from_shp_file

# Adding the root directory to the system path
sys.path.append('../..')

# Modules from your project
import Modules.Main.image_downloading as image_downloading
from Modules.Trees.predict_with_trained_model import get_tree_mask_from_image
from Modules.Slopes.slopes import get_slopes_mask, mask_pixels_from_slopes
from Modules.GUI import gui
from Modules.AreaFilter.Filterspecks import FilterSpecks
from Modules.AreaFilter.RectangleFilter import detect_rectangles,smooth_unwanted

import math
import openpyxl
import time

DTM_FILE_PATH = "../../DTM_data/DTM_new/dtm_mimad_wgs84utm36_10m.tif"
trained_model_path = "../../Models/our_models/official_masks_10%.joblib"  # The trained model


def get_image_from_utm(coordinates: Tuple[float, float], km_radius: float) -> Tuple[str, np.ndarray]:
    with open("preferences.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())
    lat, long = image_downloading.convert_to_lat_long(coordinates)  # ToDO: change to out of function as input
    img = image_downloading.download_image(lat, long, prefs["zoom"], prefs['url'], prefs['tile_size'],
                                           length=2 * km_radius)
    path = os.path.join('images_from_argcis', f'data_{coordinates[0], coordinates[1]}')
    if not os.path.exists(path):
        os.makedirs(path)
    name = f'images_from_argcis/data_{coordinates[0], coordinates[1]}/img_{coordinates[0], coordinates[1]}.png'
    cv2.imwrite(name, img)
    print("image downloaded")

    return name, img


def get_building_image_from_utm(coordinates: Tuple[float, float], km_radius: float) -> np.ndarray:
    with open("preferences_building.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())
    lat, long = image_downloading.convert_to_lat_long(coordinates)
    img = image_downloading.download_image(lat, long, prefs["zoom"], prefs['url'], prefs['tile_size'],
                                           length=2 * km_radius)
    path = os.path.join('images_from_argcis', f'data_{coordinates[0], coordinates[1]}')
    if not os.path.exists(path):
        os.makedirs(path)
    name = f'images_from_argcis/data_{coordinates[0], coordinates[1]}/img_buildings_{coordinates[0], coordinates[1]}.png'
    cv2.imwrite(name, img)
    print("Building image downloaded")
    return img


def overlay_masks(e_vals: np.ndarray, n_vals: np.ndarray, e_center: float, n_center: float, m_radius: float,
                  trees: np.ndarray, slopes: np.ndarray) -> np.ndarray:
    row_tree = np.round((n_vals - n_center + m_radius) / (2 * m_radius) * trees.shape[0]).astype(int)
    col_tree = np.round((e_vals - e_center + m_radius) / (2 * m_radius) * trees.shape[1]).astype(int)
    row_slope = np.round((n_vals - n_center + m_radius) / (2 * m_radius) * slopes.shape[0]).astype(int) - 1
    col_slope = np.round((e_vals - e_center + m_radius) / (2 * m_radius) * slopes.shape[1]).astype(int) - 1
    tree = trees[row_tree, col_tree]
    slope = slopes[row_slope, col_slope]
    and_mask = np.logical_and(tree == VIABLE_LANDING, slope == VIABLE_LANDING)
    return np.where(and_mask, VIABLE_LANDING, UNVIABLE_LANDING)


def get_total_mask_from_masks(e_center: float, n_center: float, radius: float, trees_mask: np.ndarray,
                              slopes_mask: np.ndarray) -> np.ndarray:
    m_radius = int(radius * 1000)
    e_vals = np.arange(e_center - m_radius, e_center + m_radius)
    n_vals = np.arange(n_center - m_radius, n_center + m_radius)

    # Create 2D arrays of e and n values for indexing
    ee, nn = np.meshgrid(e_vals, n_vals, indexing='xy')

    # Calculate the total mask using vectorized numpy indexing
    total_mask = overlay_masks(ee, nn, e_center, n_center, m_radius, trees_mask, slopes_mask)

    return total_mask


def plot_image_and_mask(image_to_predict: str, predicted_mask_tree: np.ndarray, predicted_mask_slope: np.ndarray,
                        total_mask: np.ndarray, coordinates: Tuple[float, float]) -> None:
    # This part is only plotting style:
    # plots predicted and original images
    # side-by-side plot of the tile and the masks
    fig, axes = plt.subplots(2, 2)
    # with rio.open(img_filepath) as src:
    with rio.open(image_to_predict) as src:
        plot.show(src.read(), ax=axes[0][0])
    axes[0][0].set_title("Image: " + str(coordinates))
    axes[1][0].set_title("tree mask")
    axes[1][0].imshow(predicted_mask_tree, cmap='Greys', interpolation='nearest')
    axes[1][1].set_title("slopes mask")
    axes[1][1].imshow(predicted_mask_slope, cmap='Greys', interpolation='nearest')
    axes[0][1].set_title("total mask")
    axes[0][1].imshow(total_mask, cmap='Greys', interpolation='nearest')
    saved_image_name = str(int(coordinates[0])) + "," + str(int(coordinates[1])) + " RESULT"
    #plt.savefig(os.path.join("results_images", saved_image_name))
    plt.show()


def get_viable_landing_in_radius(coordinates: Tuple[float, float], km_radius: float, screen_gui: gui) -> Tuple[
    np.ndarray, Dict[str, np.ndarray]]:
    st = time.time()
    cputime_start = time.process_time()
    # TODO: improve modularity, allow user to add or implement more mask functions
    building_image = get_building_image_from_utm(coordinates, km_radius)
    building_mask = get_building_mask(building_image)
    # building_mask = enlarge_obstacles(building_mask)
    building_mask = filter_chopper_area(building_mask, 30, 30)
    slopes_mask = get_slopes_mask(coordinates, km_radius)

    image_name, img = get_image_from_utm(coordinates, km_radius)
    shp_mask = get_mask_from_shp_file(SHP_PATH, coordinates, km_radius, (img.shape[0], img.shape[1]))
    tree_shape = img.shape
    unwanted_pixels_slope = mask_pixels_from_slopes(slopes_mask, tree_shape,
                                                    slopes_mask.shape)  # add according to slopes - find all places where slope is 1
    unwanted_pixels = unwanted_pixels_slope  # TODO: add mask pixels from building also fo
    screen_gui.update_progressbar_speed(slopes_mask)

    tree_mask = get_tree_mask_from_image(image_name, unwanted_pixels)
    tree_and_slope_mask = get_total_mask_from_masks(coordinates[0], coordinates[1], km_radius, tree_mask,
                                                    slopes_mask)
    total_mask = get_total_mask_from_masks(coordinates[0], coordinates[1], km_radius, building_mask,
                                           tree_and_slope_mask)

    
    total_mask = smooth_unwanted(total_mask,(30,50))
    filter_area_size = 750
    total_mask_filtered = FilterSpecks(total_mask, filter_area_size)
    data_analyse(slopes_mask, km_radius, st, cputime_start)
    print("Finish")
    # plot_image_and_mask(image_name, building_mask, tree_and_slope_mask,
    #                     total_mask, coordinates)
    screen_gui.update_progressbar(100)
    masks_dictionary = {"Slopes": slopes_mask, "Trees": tree_mask,
                        "Slopes&Trees": tree_and_slope_mask,
                        "Buildings": building_mask, "Electricity": shp_mask,
                        "Buildings&Slopes&Trees": total_mask_filtered}  # TODO: add building mask and fix colors
    return img, masks_dictionary


if __name__ == '__main__':
    # BoundingBox(left=692125.0, bottom=3614785.0, right=705335.0, top=3623875.0) Yokneam
    # BoundingBox(left=684825.0, bottom=3621765.0, right=689175.0, top=3624175.0) some
    # BoundingBox(left=666735.0, bottom=3590995.0, right=852765.0, top=3823815.0) top
    screen = gui.GUI()
    screen.mainloop()
    coordinates = (698812, 3620547, 36, 'N')
    km_radius = 0.2
    # #
    # # 698342,3618731
    # # 698812,3620547
    # # 740000,3726000
    # 695812,3600547
    # 697687, 3620721
    # 668668, 3542197 building test
    # get_viable_landing_in_radius(coordinates, km_radius,screen)
