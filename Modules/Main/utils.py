import json
from typing import Tuple, List

import cv2
import numpy as np
import functools
import rasterio as rio
from matplotlib import pyplot as plt
from rasterio import plot

from Modules.GUI.settings import *
from Modules.Main import image_downloading

WHITE = 255
BLACK = 0


def create_circular_structuring_element(radius: int) -> np.ndarray:
    """
    Creates a circular structuring element with the given radius, to be used in cv2.dilate because cv2's is wrong
    :param radius: radius of the circle
    :return: 0 or 1 in each pixel, 1 in the pixels that are in the circle
    """
    diameter = 2 * radius + 1
    center = (radius, radius)
    structuring_element = np.zeros((diameter, diameter), dtype=np.uint8)
    cv2.circle(structuring_element, center, radius, 1, -1)
    return structuring_element


def enlarge_obstacles(image: np.ndarray, radius: int = 0) -> np.ndarray:
    """
    We dilate the white areas with the cv2.dilate func, so if our viable landing is white, we invert, because we want to
    dilate the invalid areas
    :param image: binary image, 0 for black, 255 for white
    :param radius: required distance between obstacles and landing site
    :return: image with bigger obstacles, to ensure safe landing
    """
    if radius <= 0:
        print("No enlargement done, radius is non-positive")
        return image
    kernel = create_circular_structuring_element(radius)
    if VIABLE_LANDING == WHITE and UNVIABLE_LANDING == BLACK:
        inverted = cv2.bitwise_not(image)
        dilated = cv2.dilate(inverted, kernel, iterations=1)
        enlarged = cv2.bitwise_not(dilated)
    elif VIABLE_LANDING == BLACK and UNVIABLE_LANDING == WHITE:
        dilated = cv2.dilate(image, kernel, iterations=1)
        enlarged = dilated
    else:
        raise ValueError("VIABLE_LANDING and UNVIABLE_LANDING must be either 0 or 255")
    return enlarged


def filter_chopper_area(array, radius=15):
    """
    Highlight all areas that a chopper could be in.
    First, enlarge the obstacles by a radius of wingspan/2, to find locations fit for the center of the chopper.
    Then invert enlarge invert to enlarge the centers again, to find locations fit for the wings of the chopper.
    :param array: binary mask with VIABLE_LANDING and UNVIABLE_LANDING pixels
    :param radius: radius of the chopper
    :return: binary mask with VIABLE_LANDING in pixels that could fit the chopper, UNVIABLE_LANDING otherwise
    """
    array = enlarge_obstacles(array, radius=radius)
    array = cv2.bitwise_not(array)
    array = enlarge_obstacles(array, radius=radius)
    array = cv2.bitwise_not(array)
    return array


def calculate_new_speed_run(slopes_mask, km_radius):
    """
    calculates the new speed run based on the slopes mask and the radius
    :param slopes_mask:
    :param km_radius:
    :return:
    """
    count_good_pixels = np.count_nonzero(slopes_mask == VIABLE_LANDING)
    slopy = 100 * count_good_pixels / slopes_mask.size
    time_for_flat_km_area = 300
    new_area = ((2 * float(km_radius)) ** 2) * (slopy / 100)
    time_for_iteration = new_area * time_for_flat_km_area / 100
    return time_for_iteration


def cache_result(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args in cache:
            # Return the cached result if it exists
            return cache[args]

        # Perform the slow operation
        result = func(*args)

        # Cache the result
        cache[args] = result

        return result

    return wrapper


# TODO: Every single instance of coordinates is the wrong typing
def get_layer_from_server(coordinates: Tuple[int, int, int, str], km_radius: float, url_name: str,
                          inner_folder_name: str,
                          folder_name: str = 'images_from_arcgis') -> Tuple[str, np.ndarray]:
    """
    return a layer from the arcgis server based on a url in arcgis_preferences.json, and save it in a folder
    :param coordinates: the utm coordinates of the center of the area
    :param km_radius: radius in km
    :param url_name: name of the url in arcgis_preferences.json
    :param inner_folder_name: name of the folder to save the image in
    :param folder_name: defaults to 'images_from_arcgis', could change in future
    :return:
    """
    with open("arcgis_preferences.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())
    lat, long = image_downloading.convert_to_lat_long(coordinates)
    img = image_downloading.download_image(lat, long, prefs["zoom"], prefs[url_name], prefs['tile_size'],
                                           length=2 * km_radius)
    path = os.path.join(folder_name, f'data_{coordinates[0], coordinates[1]}')
    if not os.path.exists(path):
        print("Creating folder for data")
        os.makedirs(path)
    name = f'{folder_name}/data_{coordinates[0], coordinates[1]}/{inner_folder_name}_{coordinates[0], coordinates[1]}.png'
    cv2.imwrite(name, img)
    print("Building image downloaded")
    return name, img


def stretch_array(input_array: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Stretches an array to a target size using nearest neighbor interpolation
    :param input_array: 2D array to be stretched
    :param target_size: size we want to stretch to
    :return: stretched array
    """
    stretch_ratio_x = target_size[1] / input_array.shape[1]
    stretch_ratio_y = target_size[0] / input_array.shape[0]
    x = np.arange(target_size[1])
    y = np.arange(target_size[0])
    grid_x, grid_y = np.meshgrid(x, y)
    input_x = (grid_x / stretch_ratio_x).astype(int)
    input_y = (grid_y / stretch_ratio_y).astype(int)
    return input_array[input_y, input_x]


def change_resolution_of_mask(mask, image_size):
    """
    :param mask:  mask
    :param image_size: the new size of the mask
    :return:
    """
    mask = mask.astype(np.uint8)
    mask = cv2.resize(mask, image_size, interpolation=cv2.INTER_NEAREST)
    return mask


def get_total_mask_from_masks(masks: List[np.ndarray], km_radius: float) -> np.ndarray:
    """
    Overlay the masks on top of each other and return the total mask
    :param masks: list of masks
    :param km_radius: radius of the image
    :return: the total mask
    """
    # Resize all masks to the same size of km_radius * 1000 * 2 by km_radius * 1000 * 2
    m_radius = int(km_radius * 1000)
    # TODO: maybe use Matan's stretch_array
    resized_masks = [stretch_array(mask.astype(np.uint8), (2 * m_radius, 2 * m_radius)) for mask in masks]
    if VIABLE_LANDING == WHITE and UNVIABLE_LANDING == BLACK:
        total_mask = np.logical_and.reduce(resized_masks)
    elif VIABLE_LANDING == BLACK and UNVIABLE_LANDING == WHITE:
        total_mask = np.logical_or.reduce(resized_masks)
    else:
        raise ValueError("VIABLE_LANDING and UNVIABLE_LANDING must be either 0 or 255")
    total_mask = np.where(total_mask, VIABLE_LANDING, UNVIABLE_LANDING)
    return total_mask


def plot_image_and_mask(image_to_predict: str, predicted_mask_tree: np.ndarray, predicted_mask_slope: np.ndarray,
                        total_mask: np.ndarray, coordinates: Tuple[int, int, int, str]) -> None:
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
    # plt.savefig(os.path.join("results_images", saved_image_name))
    plt.show()


@cache_result
def get_image_from_utm(coordinates: Tuple[int, int, int, str], km_radius: float) -> Tuple[str, np.ndarray]:
    return get_layer_from_server(coordinates, km_radius, 'aerial_url', 'img')


def get_building_image_from_utm(coordinates: Tuple[int, int, int, str], km_radius: float) -> Tuple[str, np.ndarray]:
    return get_layer_from_server(coordinates, km_radius, 'building_url', 'img_buildings')


def mask_pixels_from_slopes(slopes_mask_in_black_and_white: np.ndarray, tree_shape: Tuple[int, int],
                            slope_shape: Tuple[int, int]) -> np.ndarray:

    slope2TreeRow = tree_shape[0] / slope_shape[0]
    slope2TreeCol = tree_shape[1] / slope_shape[1]

    tree_mask = np.zeros((tree_shape[0], tree_shape[1]), dtype=bool)
    masked_pixels_slope = np.argwhere(slopes_mask_in_black_and_white == UNVIABLE_LANDING)  # guessed 0 is black in rgb
    for index in masked_pixels_slope:
        first_row, last_row = math.floor(slope2TreeRow * index[0]), math.ceil((slope2TreeRow) * (index[0] + 1) + 1)
        first_col, last_col = math.floor(slope2TreeCol * index[1]), math.ceil((slope2TreeCol) * (index[1] + 1) + 1)
        tree_mask[first_row:last_row, first_col:last_col] = True
    masked_pixels_tree = np.argwhere(tree_mask == True)
    # move the pixels of trees

    return masked_pixels_tree


