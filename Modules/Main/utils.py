import cv2
import numpy as np

from Modules.GUI.settings import *

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


def enlarge_obstacles(image: np.ndarray, radius: int = 8) -> np.ndarray:
    """
    We dilate the white areas with the cv2.dilate func, so if our viable landing is white, we invert, because we want to
    dilate the invalid areas
    :param image: binary image, 0 for black, 255 for white
    :param radius: required distance between obstacles and landing site
    :return: image with bigger obstacles, to ensure safe landing
    """
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


def OUT_OF_USE_area_filter(array, m, n):
    """
    Legacy function, not used anymore
    :param array:
    :param m:
    :param n:
    :return:
    """
    horizontal_sum = np.cumsum(array, axis=0)
    integral_image = np.cumsum(horizontal_sum, axis=1)
    region_sums = np.zeros_like(array)
    integral_image = np.pad(integral_image, ((0, 1), (0, 1)), mode='constant')
    rows = np.arange(m - 1, array.shape[0])
    cols = np.arange(n - 1, array.shape[1])
    region_sums[rows[:, np.newaxis], cols] = integral_image[rows[:, np.newaxis], cols] - \
                                             integral_image[rows[:, np.newaxis] - m, cols] - \
                                             integral_image[rows[:, np.newaxis], cols - n] + \
                                             integral_image[rows[:, np.newaxis] - m, cols - n]
    mask = (region_sums == m * n)
    expanded_mask = np.zeros_like(array)
    ones_locations = np.where(mask)
    for i in range(len(ones_locations[0])):
        print(i / len(ones_locations[0]))
        for k in range(m):
            for l in range(n):
                expanded_mask[ones_locations[0][i] - k, ones_locations[1][i] - l] = 1
        result = array * expanded_mask
        return result
