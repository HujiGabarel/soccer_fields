import matplotlib.pyplot as plt
import numpy as np


def get_image_from_utm(coordinates):
    """Returns an image from the coordinates"""
    pass


def get_tree_mask_from_image(aerial):
    pass


def get_partial_dtm_from_utm(coordinates):
    pass


def get_total_mask_from_masks(tree_mask, heights_mask):
    pass


def get_heights_mask_from_dtm(dtm):
    pass


def get_viable_landing_in_radius(coordinates, radius = 1):
    # LOOP OVER ALL THE COORDINATES IN THE RADIUS
    #     aerial = get_image_from_utm(coordinates)
    #     tree_mask = get_tree_mask_from_image(aerial)
    #     dtm = get_partial_dtm_from_utm(coordinates)
    #     heights_mask = get_heights_mask_from_dtm(dtm)
    #     total_mask = get_total_mask_from_masks(tree_mask, heights_mask)
    #     plt.imshow(total_mask)
    pass


if __name__ == '__main__':
    coordinates = (0, 0)
    get_viable_landing_in_radius(coordinates)


