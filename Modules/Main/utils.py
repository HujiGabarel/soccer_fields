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
    We dilate the white areas with the cv2.dilate func, so if our viable landing is white, we invert, because we want to dilate the invalid areas
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
