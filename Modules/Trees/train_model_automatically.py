import detectree as dtr
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot
from os import path
from joblib import dump, load


def create_model_and_test_image(image_directory, mask_directory, percentage_for_train):
    """
    train model on a given data from directories and then polt test image
    :param image_directory: name of directory - string
    :param mask_directory: name of directory - string
    :param percentage_for_train: number between 0 and 100

    :return: None
    """
    # select the training tiles from the tiled aerial imagery dataset
    ts = dtr.TrainingSelector(img_dir='Forest Segmented/' + image_directory)
    split_df = ts.train_test_split(method='cluster-I', train_prop=(percentage_for_train / 100))
    # We save split_df data because we want to know which files we need to use for the testing (in predict file)
    dump(split_df, 'Models/split_df_with_' + percentage_for_train + '%.joblib')
    # train a tree/non-tree pixel classfier
    clf = dtr.ClassifierTrainer().train_classifier(
        split_df=split_df, response_img_dir='Forest Segmented/' + mask_directory)  # mask

    # save the model to 'trained_model.joblib'
    dump(clf, 'Models/trained_model_with_' + percentage_for_train + '%.joblib')

    # This part is irrelevant because we are doing this part in predict file.
    # # use the trained classifier to predict the tree/non-tree pixels
    # take_images_not_trained = split_df.loc[~split_df['train']]
    # test_filepath = take_images_not_trained.sample(1).iloc[0]['img_filepath']  # chose the filepath for test
    # # test_filepath = split_df[~split_df['train'].sample(1).iloc[0]['img_filepath']] # iloc - take row i, sample - take one random


if __name__ == '__main__':
    """
    In this file, we enter the images, their masks, and the percentage for the train.
    After the training is finished, we save a trained model. 
    We also save the images that are going to be for the testing (in split_df)
    """

    image_directory = 'all_images_tif'
    mask_directory = 'all_masks_tif'
    # need to add the file check!

    percentage_for_train = 98  # Decide according to what percentage of the information we want to train.
    create_model_and_test_image(image_directory, mask_directory, percentage_for_train)
