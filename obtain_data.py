import os
import cv2

IMG_PREFIX = "sat"
MASK_PREFIX = "mask"
DEFAULT_IMAGES_FILEPATH = "Forest Segmented/images"
DEFAULT_MASKS_FILEPATH = "Forest Segmented/masks"
MASK = True
IMAGE = False


def make_tif_from_images(image_and_paths, is_masks, dest_folder):
    """
    This function takes a set of loaded images and their file paths, and saves them in a new folder as a .tif
    if the images are masks, make them binary and change their name to match the prev image
    :param image_and_paths: 2 columns that save the images, and the paths
    :param is_masks: boolean
    :param dest_folder: folder where the images came from
    :return: void
    """
    os.mkdir(dest_folder)
    for i in range(len(image_and_paths)):
        img = image_and_paths[i][0]
        name = image_and_paths[i][1]
        if is_masks:
            img = black_and_whitefy(img)
            # NOTICE: this is correct only for the database that we have where each mask is tagged the same as
            # the image only "mask" instead of "sat"
            name = name[:name.find(MASK_PREFIX)] + IMG_PREFIX + name[name.find(MASK_PREFIX) + len(MASK_PREFIX):]
        cv2.imwrite(dest_folder + name[:name.find(".")] + ".tif", img)


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


def load_folder_to_folder(is_mask_folder, masks_filepath=DEFAULT_MASKS_FILEPATH,
                          images_filepath=DEFAULT_IMAGES_FILEPATH):
    if is_mask_folder:
        source = masks_filepath
    else:
        source = images_filepath
    dest = source + '_processed/'
    make_tif_from_images(load_images_from_folder(source), is_mask_folder, dest)


if __name__ == '__main__':
    # format of file is directory masks and images
    # load_folder_to_folder(IMAGE)
    # load_folder_to_folder(MASK)
    load_folder_to_folder(MASK, 'Forest Segmented/some_manual_masks')
