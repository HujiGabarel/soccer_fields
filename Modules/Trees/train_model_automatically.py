import detectree as dtr
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot
from os import path
from joblib import dump, load


def create_model_and_test_image(image_directory, mask_directory):
    """
    train model on a given data from directories and then polt test image
    :param image_directory: name of directory - string
    :param mask_directory: name of directory - string
    :return:
    """
    # select the training tiles from the tiled aerial imagery dataset
    ts = dtr.TrainingSelector(img_dir='Forest Segmented/' + image_directory)
    split_df = ts.train_test_split(method='cluster-I',train_prop=0.98)
    dump(split_df, 'Models/split_df_with_98%.joblib')

    # train a tree/non-tree pixel classfier
    clf = dtr.ClassifierTrainer().train_classifier(
        split_df=split_df, response_img_dir='Forest Segmented/' + mask_directory)  # mask

    # save the model to 'trained_model.joblib'
    dump(clf, 'Models/trained_model_with_98%.joblib')

    # use the trained classifier to predict the tree/non-tree pixels
    take_images_not_trained = split_df.loc[~split_df['train']]
    test_filepath = take_images_not_trained.sample(1).iloc[0]['img_filepath']  # chose the filepath for test
    # test_filepath = split_df[~split_df['train'].sample(1).iloc[0]['img_filepath']] # iloc - take row i, sample - take one random
    y_pred = dtr.Classifier().classify_img(test_filepath, clf)  # prediect using the model

    # side-by-side plot of the tile and the predicted tree/non-tree pixels
    figwidth, figheight = plt.rcParams['figure.figsize']
    fig, axes = plt.subplots(1, 2, figsize=(2 * figwidth, figheight))

    # with rio.open(img_filepath) as src:
    with rio.open(test_filepath) as src:
        plot.show(src.read(), ax=axes[0])
    axes[1].set_title(test_filepath)
    axes[1].imshow(y_pred)
    plt.show()


if __name__ == '__main__':
    create_model_and_test_image('all_images_tif', 'all_masks_tif')
