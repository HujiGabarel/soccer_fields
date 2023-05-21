import cv2
import numpy as np
def smooth(building_mask):
    return cv2.morphologyEx(building_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))


def get_building_mask(building_image):
    # run over each pixel and check if it is a in range of rgb of [220, 220, 220]
    # if it is, change it to 1, else change it to 0
    # return the mask
    # 255 is building, 0 is not building
    range_fiter = range(210, 225)
    building_mask = np.copy(building_image)
    for i in range(building_mask.shape[0]):
        for j in range(building_mask.shape[1]):
            if building_mask[i][j][0] in range_fiter and building_mask[i][j][1] in range_fiter and building_mask[i][j][
                2] in range_fiter:
                building_mask[i][j] = 255
            else:
                building_mask[i][j] = 0
    # convert to grayscale
    return cv2.cvtColor(smooth(building_mask), cv2.COLOR_BGR2GRAY)