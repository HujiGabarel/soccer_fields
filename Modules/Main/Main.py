import sys

from Modules.Main.Processing_runtimes import data_analyse
from Modules.Main.utils import *
from Modules.SHP_Handle.read_shp import get_mask_from_shp_file

# Adding the root directory to the system path
sys.path.append('../..')

# Modules from your project
from Modules.Trees.predict_with_trained_model import get_tree_mask
from Modules.Slopes.slopes import get_slopes_mask
from Modules.GUI import gui
from Modules.Building.Buildings import get_building_mask
import time

DEFAULT_FUNCS = [get_slopes_mask, get_building_mask, get_tree_mask]


def get_viable_landing_in_radius(coordinates: Tuple[int, int, int, str], km_radius: float,
                                 get_mask_functions=None) -> Tuple[np.ndarray, List[np.ndarray]]:
    """
    Given coordinates and radius, return an image of the area, with masks of all the obstacles in the area.
    :param coordinates: UTM coordinates
    :param km_radius: radius in km
    :param get_mask_functions: list of functions that return a mask
    :return: image of the area, list of masks
    """
    if get_mask_functions is None:
        get_mask_functions = DEFAULT_FUNCS
    st = time.time()
    cputime_start = time.process_time()
    distances = [0, 50, 0]
    image_name, img = get_image_from_utm(coordinates, km_radius)
    total_masks = [np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * VIABLE_LANDING]
    for get_some_mask in get_mask_functions:
        # TODO: we have a bug here, if we enlarge the tree mask, we enlarge other obstacles as well, we need to
        #  subtract masks to find only the new trees and enlarge them.
        partial_mask = get_some_mask(coordinates, km_radius, total_masks[-1])
        partial_mask = enlarge_obstacles(partial_mask.astype(np.uint8),
                                         distances[get_mask_functions.index(get_some_mask)])
        total_mask = get_total_mask_from_masks([total_masks[-1], partial_mask], km_radius)
        # TODO: add support for live speed updates
        # screen_gui.update_progressbar_speed(calculate_new_speed_run(total_mask, km_radius))
        total_masks.append(total_mask)
    shp_mask = get_mask_from_shp_file(SHP_PATH, coordinates, km_radius, (img.shape[0], img.shape[1]))
    # could select of the following two filters
    # total_mask_big_spots = smooth_unwanted(total_mask, (15, 5))
    total_masks[-1] = filter_chopper_area(total_masks[-1].astype(np.uint8), radius=15)
    name = f'images_from_arcgis/data_{coordinates[0], coordinates[1]}/mask_{coordinates[0], coordinates[1]}.png'
    cv2.imwrite(name, total_masks[-1])
    data_analyse(total_masks[-2], km_radius, st, cputime_start)
    print("Finish")
    return img, total_masks[1:]


if __name__ == '__main__':
    screen = gui.GUI()
    screen.mainloop()
    coordinates = (698812, 3620547, 36, 'N')
    km_radius = 0.2
