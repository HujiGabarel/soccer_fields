import os

import numpy as np
from joblib import dump, load

from Modules.Main.utils import get_image_from_utm, mask_pixels_from_slopes
from Modules.Trees.classifier import Classifier
import rasterio as rio
from rasterio import plot
from Modules.GUI.settings import *
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt

"""
This file load trained model and predict for given image
"""


def predict(trained_model_name, image_name, images_directory):
    """
    """
    # load the trained model
    trained_model = load(trained_model_name)
    # use the trained model on the image for prediction
    image_to_predict = os.path.join(images_directory, image_name)
    predicted_mask = Classifier(refine=False).classify_img(image_to_predict, trained_model)
    # Plot
    trained_model_title = file_name_to_title(trained_model_name)
    image_title = file_name_to_title(image_name)
    plot_image_and_mask(image_to_predict, predicted_mask, image_title, trained_model_title)
    # Saving the images (side by side view)
    save_plot(trained_model_title, image_title, images_directory)


def predict_image(image_to_predict, trained_model_path, pixels_to_ignore):
    trained_model = load(trained_model_path)
    predicted_mask = Classifier().classify_img(image_to_predict, trained_model, pixels_to_ignore)

    # plot_image_and_mask(image_to_predict,predicted_mask, image_title="", trained_model_title="")
    # plt.show()
    # when we get here, 0 represents nontree, 255 is tree
    return predicted_mask


def file_name_to_title(file_name):
    # "your_mom/Matan_is_the_king.png" -> "Matan_is_the_king"
    file_name = file_name.split('/')[-1]  # remove the path of the file
    title = '.'.join(file_name.split('.')[:-1])  # remove the end of the file
    return title


def plot_image_and_mask(image_to_predict, predicted_mask, image_title, trained_model_title, ):
    # This part is only plotting style:
    # plots predicted and original images
    # side-by-side plot of the tile and the predicted tree/non-tree pixels
    figwidth, figheight = plt.rcParams['figure.figsize']
    fig, axes = plt.subplots(1, 2, figsize=(2 * figwidth, figheight), sharex="all", sharey="all")
    # with rio.open(img_filepath) as src:
    with rio.open(image_to_predict) as src:
        plot.show(src.read(), ax=axes[0])
    axes[0].set_title("Model: " + trained_model_title)
    axes[1].set_title("Image: " + image_title)
    axes[1].imshow(predicted_mask)


def save_plot(trained_model_title, image_title, images_directory):
    # create new directory for the result images
    # And save the results
    results_directory_name = "Result of " + trained_model_title
    path = os.path.join(images_directory, results_directory_name)

    exists = os.path.exists(path)
    if not exists:  # Create a new directory because it does not exist
        os.makedirs(path)
    # Save figure
    plt.savefig(os.path.join(path, "Result of " + image_title))
    plt.show()


def get_tree_mask_from_image(aerial: str, pixels_to_ignore, trained_model_path=TRAINED_MODEL_PATH):
    '''
    Get the aerial image, return formatted mask of the trees
    :param aerial: aerial image
    :param trained_model_path: model to predict the trees
    :param pixels_to_ignore: pixels to automatically ignore, to improve runtime
    :return: formatted mask of the trees, 255 is not tree, 0 is tree
    '''
    flipped_image = predict_image(aerial, trained_model_path, pixels_to_ignore)
    return np.where(flipped_image == UNVIABLE_LANDING, VIABLE_LANDING, UNVIABLE_LANDING)


def get_tree_mask(coordinates: Tuple[int, int, int, str], km_radius: float, total_mask=None,
                  trained_model_path: str = TRAINED_MODEL_PATH):
    image_name, img = get_image_from_utm(coordinates, km_radius)
    tree_shape = img.shape
    unwanted_pixels_slope = mask_pixels_from_slopes(total_mask, tree_shape,
                                                    total_mask.shape)  # add according to slopes - find all places where slope is 1
    unwanted_pixels = unwanted_pixels_slope  # TODO: add mask pixels from building also fo
    tree_mask = get_tree_mask_from_image(image_name, unwanted_pixels, trained_model_path)
    return tree_mask



if __name__ == '__main__':
    trained_model_path = "../../Models/official_masks_10%.joblib"  # The trained model
    images_directory = '../../Forest Segmented/from google'  # The directory of the images that the program will predict
    for image_name in os.listdir(images_directory):
        predict(trained_model_path, image_name, images_directory)
