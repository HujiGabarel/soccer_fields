
import detectree as dtr
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot
from os import path

# select the training tiles from the tiled aerial imagery dataset
ts = dtr.TrainingSelector(img_dir='Forest Segmented/some_images_tif')
split_df = ts.train_test_split(method='cluster-I')

# train a tree/non-tree pixel classfier
clf = dtr.ClassifierTrainer().train_classifier(
    split_df=split_df, response_img_dir='Forest Segmented/some_masks_tif') # mask

# use the trained classifier to predict the tree/non-tree pixels
trysplit=split_df.loc[~split_df['train']]
test_filepath = trysplit.sample(1).iloc[0]['img_filepath']
#test_filepath = split_df[~split_df['train'].sample(1).iloc[0]['img_filepath']] # iloc - take row i, sample - take one random
y_pred = dtr.Classifier().classify_img(test_filepath, clf)



# side-by-side plot of the tile and the predicted tree/non-tree pixels
figwidth, figheight = plt.rcParams['figure.figsize']
fig, axes = plt.subplots(1, 2, figsize=(2 * figwidth, figheight))

# with rio.open(img_filepath) as src:
with rio.open(test_filepath) as src:
    plot.show(src.read(), ax=axes[0])
axes[1].set_title(test_filepath)
axes[1].imshow(y_pred)
plt.show()

