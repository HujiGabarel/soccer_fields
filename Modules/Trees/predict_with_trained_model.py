import os

from joblib import dump, load
from Modules.Trees.classifier import Classifier
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot
from os import path
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
    plot_image_and_mask(image_to_predict,predicted_mask, image_title, trained_model_title)
    # Saving the images (side by side view)
    save_plot(trained_model_title, image_title, images_directory)

def predict_image(image_to_predict,trained_model_path,pixels_to_ignore):

    trained_model = load(trained_model_path)
    predicted_mask = Classifier().classify_img(image_to_predict, trained_model,pixels_to_ignore)

    # plot_image_and_mask(image_to_predict,predicted_mask, image_title="", trained_model_title="")
    # plt.show()
    return predicted_mask


def file_name_to_title(file_name):
    # "your_mom/Matan_is_the_king.png" -> "Matan_is_the_king"
    file_name = file_name.split('/')[-1]  # remove the path of the file
    title = '.'.join(file_name.split('.')[:-1])  # remove the end of the file
    return title


def plot_image_and_mask(image_to_predict, predicted_mask,image_title, trained_model_title, ):
    # This part is only plotting style:
    # plots predicted and original images
    # side-by-side plot of the tile and the predicted tree/non-tree pixels
    figwidth, figheight = plt.rcParams['figure.figsize']
    fig, axes = plt.subplots(1, 2, figsize=(2 * figwidth, figheight),sharex="all", sharey="all")
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


if __name__ == '__main__':
    trained_model_path = "../../Models/our_models/official_masks_10%.joblib"  # The trained model
    images_directory = '../../Forest Segmented/from google'  # The directory of the images that the program will predict
    for image_name in os.listdir(images_directory):
        predict(trained_model_path, image_name, images_directory)
