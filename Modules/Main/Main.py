import matplotlib.pyplot as plt
import numpy as np
import os
import json
import datetime
import image_downloading
import cv2
import utm

#TODO: decide about length
def get_image_from_utm(coordinates):
    """_summary_

    Args:
        coordinates (_type_): _description_
    """

    with open("preferences.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    coordinates = utm.from_latlon(coordinates[0],coordinates[1])

    lat,long = image_downloading.convert_to_lat_long(coordinates)
    img = image_downloading.download_image(lat,long,prefs["zoom"],prefs['url'] ,prefs['tile_size'],length=1.5)
    return img

    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # name = f'images_from_argcis/img_{timestamp}.png'
    # cv2.imwrite(name, img)
    # print(f'Saved as {name}')



    pass


def get_tree_mask_from_image(aerial):
    # using trees module, get the mask of the trees in black white
    pass


def get_partial_dtm_from_utm(coordinates):
    # find the area in the dtm that is relevant
    # cut around the area in a SIZE*SIZE matrix
    pass


def get_total_mask_from_masks(tree_mask, heights_mask):
    # return tree_mask * heights_mask
    pass


def get_slopes_mask_from_dtm(dtm):
    # get heights from the dtm
    # get slopes from the heights
    # get mask from the slopes
    # return mask
    #TODO: SIZE of the image is constant?
    pass


def get_viable_landing_in_radius(coordinates, radius = 1):
    # LOOP OVER ALL THE COORDINATES IN THE RADIUS
    #     aerial = get_image_from_utm(coordinates)
    #     tree_mask = get_tree_mask_from_image(aerial)
    #     dtm = get_partial_dtm_from_utm(coordinates)
    #     heights_mask = get_slopes_mask_from_dtm(dtm)
    #     total_mask = get_total_mask_from_masks(tree_mask, heights_mask)
    #     plt.imshow(total_mask)
    pass


if __name__ == '__main__':
    coordinates = (32.73990959272013, 34.972588222295116)
    get_image_from_utm(coordinates)
    get_viable_landing_in_radius(coordinates)


