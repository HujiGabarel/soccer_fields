import cv2
import numpy as np
from typing import Tuple, Union

from Modules.GUI.settings import UNVIABLE_LANDING, VIABLE_LANDING
from Modules.Main.utils import get_building_image_from_utm


def smooth(building_mask: np.ndarray) -> np.ndarray:
    '''
    Smoothes the building mask, OPEN removes white surrounded by black, CLOSE removes black surrounded by white.
    :param building_mask: post processed building mask, black and white
    :return: same mask, but smoother
    '''
    building_mask = cv2.morphologyEx(building_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    building_mask = cv2.morphologyEx(building_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return building_mask


def building_image_to_mask(building_image: np.ndarray) -> np.ndarray:
    '''
    Checks if a pixel is a building based on govmap color coding.
    :param building_image: image from govmap, highlights buildings in gray
    :return: standard mask, viable or unviable landing
    '''
    range_filter = range(210, 225)
    building_mask = np.copy(building_image)
    for i in range(building_mask.shape[0]):
        for j in range(building_mask.shape[1]):
            if building_mask[i][j][0] in range_filter and building_mask[i][j][1] in range_filter and \
                    building_mask[i][j][2] in range_filter:
                building_mask[i][j] = UNVIABLE_LANDING
            else:
                building_mask[i][j] = VIABLE_LANDING
    # Convert to grayscale
    return cv2.cvtColor(smooth(building_mask), cv2.COLOR_BGR2GRAY)


def get_building_mask(coordinates: Tuple[int, int, int, str], km_radius: float, total_mask: np.ndarray) -> np.ndarray:
    _, building_image = get_building_image_from_utm(coordinates, km_radius)
    return building_image_to_mask(building_image)
