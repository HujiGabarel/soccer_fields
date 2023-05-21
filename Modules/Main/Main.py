import sys
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import rasterio
import cv2
import rasterio as rio
from rasterio import plot
import math
import openpyxl
import time

# Adding the root directory to the system path
sys.path.append('../..')

# Modules from your project
import Modules.Main.image_downloading as image_downloading
from Modules.Trees.predict_with_trained_model import predict_image
from Modules.Slopes.slopes import get_max_slopes, plot_heat_map, convert_slopes_to_black_and_white
from Modules.GUI import gui
from Modules.AreaFilter.Filterspecks import FilterSpecks
from Modules.AreaFilter.RectangleFilter import detect_rectangles

# Constants
DTM_FILE_PATH = "../../DTM_data/DTM_new/dtm_mimad_wgs84utm36_10m.tif"
trained_model_path = "../../Models/our_models/official_masks_10%.joblib"  # The trained model


# TODO: decide about length
def get_image_from_utm(coords: Tuple[float, float], km_radius: float) -> Tuple[str, np.ndarray]:
    with open("preferences.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())
    lat, long = image_downloading.convert_to_lat_long(coords)
    print(lat, long)
    img = image_downloading.download_image(lat, long, prefs["zoom"], prefs['url'], prefs['tile_size'],
                                           length=2 * km_radius)
    print("image downloaded")
    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'images_from_argcis/img_{coords[0], coords[1]}.png'
    cv2.imwrite(name, img)
    print(f'Saved as {name}')
    return name, img


# TODO: repetitive code, mix the preferences files
def get_building_image_from_utm(coordinates: Tuple[float, float], km_radius: float) -> np.ndarray:
    with open("preferences_building.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())
    lat, long = image_downloading.convert_to_lat_long(coordinates)
    print(lat, long)
    img = image_downloading.download_image(lat, long, prefs["zoom"], prefs['url'], prefs['tile_size'],
                                           length=2 * km_radius)
    print("image downloaded")
    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'images_from_argcis/img_{coordinates[0], coordinates[1]}.png'
    cv2.imwrite(name, img)
    print(f'Saved as {name}')
    return img


def smooth(img: np.ndarray) -> np.ndarray:
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def building_image_to_building_mask(building_image: np.ndarray) -> np.ndarray:
    '''
    Get the buildings image, return formatted mask of the buildings
    :param building_image: regular image of the buildings
    :return: mask of the buildings, 255 is not building, 0 is building
    '''
    range_filter = range(210, 225)
    image = np.copy(building_image)
    mask = np.all(np.isin(image, range_filter), axis=2)
    image[mask] = 0
    image[~mask] = 255
    return cv2.cvtColor(smooth(image), cv2.COLOR_BGR2GRAY)


def get_tree_mask_from_image(aerial: np.ndarray, trained_model_path: str, pixels_to_ignore: List[int]) -> np.ndarray:
    '''
    Get the aerial image, return formatted mask of the trees
    :param aerial: aerial image
    :param trained_model_path: model to predict the trees
    :param pixels_to_ignore: pixels to automatically ignore, to improve runtime
    :return: formatted mask of the trees, 255 is not tree, 0 is tree
    '''
    return predict_image(aerial, trained_model_path, pixels_to_ignore)


def check_coordinates_area_are_in_dtm(coordinates: Tuple[float, float], size: float,
                                      dem: rasterio.DatasetReader) -> bool:
    return ((dem.bounds.left < (coordinates[0] + size) < dem.bounds.right) and
            (dem.bounds.left < (coordinates[0] - size) < dem.bounds.right) and
            (dem.bounds.bottom < (coordinates[1] + size) < dem.bounds.top) and
            (dem.bounds.bottom < (coordinates[1] - size) < dem.bounds.top)
            )


def mask_pixels_from_slopes(slopes_mask_in_black_and_white: np.ndarray, tree_shape: Tuple[int, int],
                            slope_shape: Tuple[int, int]) -> np.ndarray:
    unique_values, value_counts = np.unique(slopes_mask_in_black_and_white, return_counts=True)

    slope2TreeRow = tree_shape[0] / slope_shape[0]
    slope2TreeCol = tree_shape[1] / slope_shape[1]

    tree_mask = np.zeros((tree_shape[0], tree_shape[1]), dtype=bool)
    masked_pixels_slope = np.argwhere(slopes_mask_in_black_and_white == 0)  # guessed 0 is black in rgb
    for index in masked_pixels_slope:
        first_row, last_row = math.floor(slope2TreeRow * index[0]), math.ceil((slope2TreeRow) * (index[0] + 1) + 1)
        first_col, last_col = math.floor(slope2TreeCol * index[1]), math.ceil((slope2TreeCol) * (index[1] + 1) + 1)
        tree_mask[first_row:last_row, first_col:last_col] = True
    masked_pixels_tree = np.argwhere(tree_mask == True)
    print("masked", masked_pixels_tree.shape)
    # move the pixels of trees
    return masked_pixels_tree


def get_partial_dtm_from_total_dtm(coordinates: Tuple[float, float], km_radius: float, meters_per_pixel: float = 10) -> \
        Tuple[np.ndarray, int, int]:
    # find the area in the dtm that is relevant
    # cut around the area in a SIZE*SIZE matrix
    size = round(km_radius * 1000 / meters_per_pixel)
    dem = rasterio.open(DTM_FILE_PATH)  # turn .tiff file to dem format, each pixel is a height
    rows = dem.height  # number of rows
    cols = dem.width  # number of columns

    # slow solution - loading all file
    # dem_data = dem.read(1).astype("int")
    ### assuming that the coordinates[0] is cols (east / west) and coordinates[1] is rows (north / south)

    # calculating the center for partial_dtm
    if check_coordinates_area_are_in_dtm(coordinates, size, dem):
        print("coordinates are in range")
    print(dem.bounds.left, dem.bounds.top)

    col_center = round((coordinates[0] - dem.bounds.left) / meters_per_pixel)
    row_center = -round((coordinates[1] - dem.bounds.top) / meters_per_pixel)

    window = rasterio.windows.Window.from_slices((row_center - size, row_center + size),
                                                 (col_center - size, col_center + size))

    partial_dtm = dem.read(1, window=window).astype("int")  # convert height to int instead of float

    # partial_dtm = dem_data[row_center - size: row_center + size, col_center - size: col_center + size]

    new_rows = partial_dtm.shape[0]
    new_cols = partial_dtm.shape[1]

    return partial_dtm, new_rows, new_cols


def get_white_or_black(e_vals: np.ndarray, n_vals: np.ndarray, e_center: float, n_center: float, m_radius: float,
                       trees: np.ndarray, slopes: np.ndarray) -> np.ndarray:
    row_tree = np.round((n_vals - n_center + m_radius) / (2 * m_radius) * trees.shape[0]).astype(int)
    col_tree = np.round((e_vals - e_center + m_radius) / (2 * m_radius) * trees.shape[1]).astype(int)
    row_slope = np.round((n_vals - n_center + m_radius) / (2 * m_radius) * slopes.shape[0]).astype(int) - 1
    col_slope = np.round((e_vals - e_center + m_radius) / (2 * m_radius) * slopes.shape[1]).astype(int) - 1
    tree = trees[row_tree, col_tree]
    slope = slopes[row_slope, col_slope]
    mask = np.logical_and(np.logical_not(tree), slope)
    return np.where(mask, 255, 0)


def get_total_mask_from_masks(e_center: float, n_center: float, radius: float, trees: np.ndarray,
                              slopes: np.ndarray) -> np.ndarray:
    m_radius = int(radius * 1000)
    e_vals = np.arange(e_center - m_radius, e_center + m_radius)
    n_vals = np.arange(n_center - m_radius, n_center + m_radius)

    # Create 2D arrays of e and n values for indexing
    ee, nn = np.meshgrid(e_vals, n_vals, indexing='xy')

    # Calculate the total mask using vectorized numpy indexing
    total_mask = get_white_or_black(ee, nn, e_center, n_center, m_radius, trees, slopes)

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
    plt.savefig(os.path.join("results_images", saved_image_name))
    plt.show()


def update_progressbar_speed(screen_gui: gui, slopes_mask_in_black_and_white: np.ndarray) -> None:
    count_slopes_good = np.count_nonzero(slopes_mask_in_black_and_white == 255)
    slopy = 100 * count_slopes_good / slopes_mask_in_black_and_white.size
    screen_gui.set_time_for_iteration(slopy)


def get_viable_landing_in_radius(coordinates: Tuple[float, float], km_radius: float, screen_gui: gui) -> Tuple[
    np.ndarray, Dict[str, np.ndarray]]:
    st = time.time()
    cputime_start = time.process_time()
    # TODO: improve modularity, allow user to add or implement more mask functions
    # building mask
    building_image = get_building_image_from_utm(coordinates, km_radius)
    building_mask = building_image_to_building_mask(building_image)
    partial_dtm, new_rows, new_cols = get_partial_dtm_from_total_dtm(coordinates, km_radius)
    slope_shape = (new_rows, new_cols)
    slopes_mask = get_max_slopes(partial_dtm, new_rows, new_cols)
    slopes_mask_in_black_and_white = np.array(convert_slopes_to_black_and_white(slopes_mask, new_rows, new_cols))
    update_progressbar_speed(screen_gui, slopes_mask_in_black_and_white)  # TODO:fix progressbar_speed

    image_name, img = get_image_from_utm(coordinates, km_radius)
    tree_shape = img.shape
    unwanted_pixels_slope = mask_pixels_from_slopes(slopes_mask_in_black_and_white, tree_shape,
                                                    slope_shape)  # add according to slopes - find all places where slope is 1
    unwanted_pixels = unwanted_pixels_slope  # TODO: add mask pixels from building also fo
    tree_mask = get_tree_mask_from_image(image_name, trained_model_path, unwanted_pixels)
    tree_and_slope_mask = get_total_mask_from_masks(coordinates[0], coordinates[1], km_radius, tree_mask,
                                                    slopes_mask_in_black_and_white)
    total_mask = get_total_mask_from_masks(coordinates[0], coordinates[1], km_radius, building_mask,
                                           tree_and_slope_mask)
    filter_area_size = 750
    total_mask_filtered = FilterSpecks(total_mask, filter_area_size)
    data_analyse(slopes_mask_in_black_and_white, km_radius, st, cputime_start)
    print("Finish")
    plot_image_and_mask(image_name, building_mask, tree_and_slope_mask,
                        total_mask, coordinates)
    screen_gui.update_progressbar(100)
    masks_dictionary = {"Slopes": slopes_mask_in_black_and_white, "Trees": np.where(tree_mask == 255, 0, 255),
                        "Slopes&Trees": tree_and_slope_mask,
                        "Buildings": np.where(building_mask == 255, 0, 255),
                        "Buildings&Slopes&Trees": total_mask_filtered}  # TODO: add building mask and fix name
    return img, masks_dictionary


def data_analyse(slopes_mask_in_black_and_white: np.ndarray, km_radius: float, st: float, cputime_start: float) -> None:
    # count number of 255 in slopes_mask_in_black_and_white
    count_slopes_good = np.count_nonzero(slopes_mask_in_black_and_white == 255)
    slopy = round(100 * count_slopes_good / slopes_mask_in_black_and_white.size, 2)
    area = (2 * km_radius) ** 2
    total_time = time.time() - st
    cpu_total_time = time.process_time() - cputime_start
    # write to excel
    print(slopy, area, total_time)
    save_result_to_excel(slopy, area, total_time, cpu_total_time)


def save_result_to_excel(slopy: float, area: float, total_time: float, cpu_total_time: float) -> None:
    workbook = openpyxl.load_workbook("results.xlsx")
    worksheet = workbook.active
    worksheet.title = "result"
    worksheet.cell(row=1, column=1, value="slopy%")
    worksheet.cell(row=1, column=2, value="area [km^2]")
    worksheet.cell(row=1, column=3, value="total time [sec]")
    worksheet.cell(row=1, column=4, value="cpu total time [sec]")
    # add to filename
    last_row = worksheet.max_row
    worksheet.cell(row=last_row + 1, column=1, value=slopy)
    worksheet.cell(row=last_row + 1, column=2, value=area)
    worksheet.cell(row=last_row + 1, column=3, value=total_time)
    worksheet.cell(row=last_row + 1, column=4, value=cpu_total_time)

    workbook.save("results.xlsx")


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
