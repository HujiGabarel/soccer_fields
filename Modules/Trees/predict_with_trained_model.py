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
    :param path_for_result_images: The path of the directory where the all_images will be saved
    :return:
    """
    # load the trained model
    trained_model = load(trained_model_name)
    trained_model_name=trained_model_name[7:-7]
    y_pred = dtr.Classifier().classify_img(image_to_predict, trained_model)

    # plots predicted and original all_images
    # side-by-side plot of the tile and the predicted tree/non-tree pixels
    figwidth, figheight = plt.rcParams['figure.figsize']
    fig, axes = plt.subplots(1, 2, figsize=(2 * figwidth, figheight))

    # with rio.open(img_filepath) as src:
    with rio.open(image_to_predict) as src:
        plot.show(src.read(), ax=axes[0])
    axes[0].set_title(trained_model_name)
    axes[1].set_title(image_name)
    axes[1].imshow(y_pred)
    print(trained_model_name)

    path_result_directory=path_for_result_images + "\\result_" + trained_model_name+"\\"

    plt.savefig(path_result_directory+image_name[0:-4])
    plt.show()


if __name__ == '__main__':

    trained_model_name = 'Models/official_masks_10%.joblib'  # The trained model
    images_directory = "Forest Segmented\\from google"  # The directory of the all_images that the program will predict

    path_for_result_images = "C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\" +images_directory  # directory for save
    for image_name in os.listdir(images_directory):
        image_to_predict = os.path.join(images_directory, image_name)
        predict(trained_model_name, image_to_predict, image_name, path_for_result_images)
