import os

from joblib import dump, load
import detectree as dtr
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot
from os import path

"""
This file load trained model and predict for given image
"""


def predict(trained_model_name, image_to_predict, image_name, path_for_result_images):
    """

    :param trained_model_name: the name of the model (joblib)
    :param image_to_predict: the path of the image
    :param image_name: the name of the image file (joblib)
    :param path_for_result_images: The path of the directory where the images will be saved
    :return:
    """

    # load the trained model
    trained_model = load(trained_model_name)
    # use the trained model on the image for prediction
    predicted_mask = dtr.Classifier().classify_img(image_to_predict, trained_model)
    # Plot
    trained_model_title = file_name_to_title(trained_model_name)
    image_title = file_name_to_title(image_name)
    plot_image_and_mask(image_title, trained_model_title, predicted_mask)
    # Saving the images (side by side view)

    path_result_directory = images_directory + "\\result_" + trained_model_title
    os.makedirs(path_result_directory)
    plt.savefig(path_result_directory + "\\"+ image_name)
    plt.show()


def file_name_to_title(file_name):
    # "your_mom/Matan_is_the_king.png" -> "Matan_is_the_king"
    file_name = file_name.split('/')[-1]  # remove the path of the file
    title = '.'.join(file_name.split('.')[:-1])  # remove the end of the file
    return title


def plot_image_and_mask(image_title, trained_model_title, predicted_mask):
    # This part is only plotting style:
    # plots predicted and original images
    # side-by-side plot of the tile and the predicted tree/non-tree pixels
    figwidth, figheight = plt.rcParams['figure.figsize']
    fig, axes = plt.subplots(1, 2, figsize=(2 * figwidth, figheight))
    # with rio.open(img_filepath) as src:
    with rio.open(image_to_predict) as src:
        plot.show(src.read(), ax=axes[0])
    axes[0].set_title(trained_model_title)
    axes[1].set_title(image_title)
    axes[1].imshow(predicted_mask)


if __name__ == '__main__':

    trained_model_path = 'models/trained_model_with_all_images_10%.joblib'  # The trained model
    images_directory = "Forest Segmented\\from google"  # The directory of the images that the program will predict
    # "C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\"
    path_for_result_images = images_directory  # directory for save

    for image_name in os.listdir(images_directory):
        image_to_predict = os.path.join(images_directory, image_name)
        predict(trained_model_path, image_to_predict, image_name, path_for_result_images)
