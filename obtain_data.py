import os

import cv2

IMG_PREFIX = "sat"
MASK_PREFIX = "mask"


def make_tif_from_images(image_and_paths, is_masks, dest_folder):
    """
    This function takes a set of loaded images and their file paths, and saves them in a new folder
    if the images are masks, make them binary and change their name to match the prev image
    :param image_and_paths: 2 columns that save the images, and the paths
    :param is_masks: boolean
    :param dest_folder: folder where the images came from
    :return: void
    """
    for i in range(len(image_and_paths)):
        img = image_and_paths[i][0]
        name = image_and_paths[i][1]
        if is_masks:
            img = black_and_whitefy(img)
            # NOTICE: this is correct only for the database that we have where each mask is tagged the same as
            # the image only "mask" instead of "sat"
            name = name[:name.find(MASK_PREFIX)] + IMG_PREFIX + name[name.find(MASK_PREFIX) + len(MASK_PREFIX):]
        cv2.imwrite(dest_folder + name[:-3] + 'tif', img)


def load_images_from_folder(folder):
    """
    gets all the images from a folder into a list
    :param folder: folder path
    :return: images paired with their filename
    """
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, filename))
        if img is not None:
            images.append((img, filename))
    return images


def black_and_whitefy(img):
    """
    Takes an image and makes it black and white (only 0 or 255)
    :param img: RGB image
    :return: 0 or 255 image
    """
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (thresh, black_and_white_image) = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
    return black_and_white_image


if __name__ == '__main__':
    source = "Forest Segmented/some_images"
    dest = source + '_tif/'
    make_tif_from_images(load_images_from_folder(source), False, dest)
