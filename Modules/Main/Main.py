import sys
from typing import Tuple, Dict, List

import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot

from Modules.Main.Processing_runtimes import data_analyse
from Modules.Main.utils import *
from Modules.SHP_Handle.read_shp import get_mask_from_shp_file

# Adding the root directory to the system path
sys.path.append('../..')

# Modules from your project
from Modules.Trees.predict_with_trained_model import get_tree_mask_from_image
from Modules.Slopes.slopes import get_slopes_mask, mask_pixels_from_slopes
from Modules.GUI import gui
from Modules.Building.Buildings import get_building_mask
import time

DTM_FILE_PATH = "../../DTM_data/DTM_new/dtm_mimad_wgs84utm36_10m.tif"
trained_model_path = "../../Models/our_models/official_masks_10%.joblib"  # The trained model


def get_image_from_utm(coordinates: Tuple[float, float], km_radius: float) -> Tuple[str, np.ndarray]:
    return get_layer_from_server(coordinates, km_radius, 'aerial_url', 'img')


def get_building_image_from_utm(coordinates: Tuple[float, float], km_radius: float) -> Tuple[str, np.ndarray]:
    return get_layer_from_server(coordinates, km_radius, 'building_url', 'img_buildings')


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
    # plt.savefig(os.path.join("results_images", saved_image_name))
    plt.show()


def get_viable_landing_in_radius(coordinates: Tuple[float, float], km_radius: float, screen_gui: gui) -> Tuple[
    np.ndarray, Dict[str, np.ndarray]]:
    st = time.time()
    cputime_start = time.process_time()
    # TODO: improve modularity, allow user to add or implement more mask functions
    _, building_image = get_building_image_from_utm(coordinates, km_radius)
    building_mask = get_building_mask(building_image)
    building_mask = enlarge_obstacles(building_mask)
    slopes_mask = get_slopes_mask(coordinates, km_radius)
    image_name, img = get_image_from_utm(coordinates, km_radius)
    shp_mask = get_mask_from_shp_file(SHP_PATH, coordinates, km_radius, (img.shape[0], img.shape[1]))
    tree_shape = img.shape
    unwanted_pixels_slope = mask_pixels_from_slopes(slopes_mask, tree_shape,
                                                    slopes_mask.shape)  # add according to slopes - find all places where slope is 1
    unwanted_pixels = unwanted_pixels_slope  # TODO: add mask pixels from building also fo
    screen_gui.update_progressbar_speed(calculate_new_speed_run(slopes_mask, km_radius))
    tree_mask = get_tree_mask_from_image(image_name, unwanted_pixels)
    tree_and_slope_mask = get_total_mask_from_masks([tree_mask, slopes_mask], km_radius)
    total_mask = get_total_mask_from_masks([building_mask, tree_mask, slopes_mask], km_radius)
    # could select of the following two filters
    # total_mask_big_spots = smooth_unwanted(total_mask, (25, 25))
    total_mask_big_spots = filter_chopper_area(total_mask.astype(np.uint8), radius=15)
    name = f'images_from_argcis/data_{coordinates[0], coordinates[1]}/mask_{coordinates[0], coordinates[1]}.png'
    cv2.imwrite(name, total_mask_big_spots)
    data_analyse(slopes_mask, km_radius, st, cputime_start)
    masks_dictionary = {"Slopes": slopes_mask, "Trees": tree_mask,
                        "Slopes&Trees": tree_and_slope_mask,
                        "Buildings": building_mask, "Electricity": shp_mask,
                        "Buildings&Slopes&Trees": total_mask_big_spots}  # TODO: add building mask and modularity
    screen_gui.update_progressbar(100)
    print("Finish")
    return img, masks_dictionary


if __name__ == '__main__':
    screen = gui.GUI()
    screen.mainloop()
    coordinates = (698812, 3620547, 36, 'N')
    km_radius = 0.2
