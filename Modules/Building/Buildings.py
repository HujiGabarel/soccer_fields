import cv2
import numpy as np

from Modules.GUI.settings import UNVIABLE_LANDING, VIABLE_LANDING


def smooth(building_mask):
    return cv2.morphologyEx(building_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))


def get_building_mask(building_image):
    '''
    check if a pixel is a building based on govmap colorcoding
    :param building_image: image from govmap, highlights buildings in gray
    :return: standard mask, viable or unviable landing
    '''
    range_fiter = range(210, 225)
    building_mask = np.copy(building_image)
    for i in range(building_mask.shape[0]):
        for j in range(building_mask.shape[1]):
            if building_mask[i][j][0] in range_fiter and building_mask[i][j][1] in range_fiter and building_mask[i][j][
                2] in range_fiter:
                building_mask[i][j] = UNVIABLE_LANDING
            else:
                building_mask[i][j] = VIABLE_LANDING
    # convert to grayscale
    return cv2.cvtColor(smooth(building_mask), cv2.COLOR_BGR2GRAY)