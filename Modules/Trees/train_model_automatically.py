import detectree as dtr
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot
from os import path
from joblib import dump, load
import os


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
    directory_name = path_to_directory_name(image_directory)
    dump(split_df, 'Models/split_df_of_'+directory_name+'with_' + percentage_for_train + '%.joblib')
    # train a tree/non-tree pixel classfier
    clf = dtr.ClassifierTrainer().train_classifier(
        split_df=split_df, response_img_dir='Forest Segmented/' + mask_directory)  # mask

    # save the model to 'trained_model_of_xxxx_with_xx%.joblib'
    dump(clf, 'Models/trained_model_of_'+directory_name+'with_' + percentage_for_train + '%.joblib')

    # This part is irrelevant because we are doing this part in predict file.
    # # use the trained classifier to predict the tree/non-tree pixels
    # take_images_not_trained = split_df.loc[~split_df['train']]
    # test_filepath = take_images_not_trained.sample(1).iloc[0]['img_filepath']  # chose the filepath for test
    # # test_filepath = split_df[~split_df['train'].sample(1).iloc[0]['img_filepath']] # iloc - take row i, sample - take one random

def check_all_images_have_mask(image_directory, mask_directory):
    # Important: the name of the mask filename must be identical to the image filename
    images_without_mask = []
    for image_name in os.listdir(image_directory):
        if image_name not in os.listdir(mask_directory):
            images_without_mask.append(image_name)
    images_without_mask_str = ', '.join([str(elem) for elem in images_without_mask])
    return images_without_mask_str

def path_to_directory_name(path_to_directory):
    # "your_mom/Matan_is_the_king" -> "Matan_is_the_king"
    directory_name = path_to_directory.split('/')[-1]  # remove the path of the file
    return directory_name


if __name__ == '__main__':
    """
    In this file, we enter the images, their masks, and the percentage for the train.
    After the training is finished, we save a trained model. 
    We also save the images that are going to be for the testing (in split_df)
    """

    image_directory = '../../Forest Segmented/images_processed'
    mask_directory = '../../Forest Segmented/some_masks_tif'
    images_without_mask = check_all_images_have_mask(image_directory, mask_directory)
    if images_without_mask == "":
        percentage_for_train = 10  # Decide according to what percentage of the information we want to train.\
        create_model_and_test_image(image_directory, mask_directory, percentage_for_train)
    else:
        raise Exception("There is no mask for these photos: " + images_without_mask)
