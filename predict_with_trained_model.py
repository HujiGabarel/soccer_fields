from joblib import dump, load
import detectree as dtr
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot
from os import path
"""
This file load trained model and predict for given image
"""
# load the trained model
trained_model_name='0.joblib'
trained_model = load(trained_model_name)

# chose image
image_to_predict="Forest Segmented/some_images_tif\\3484_sat_23.tif" # path to image to predict

y_pred = dtr.Classifier().classify_img(image_to_predict, trained_model)

# plots predicted and original images
# side-by-side plot of the tile and the predicted tree/non-tree pixels
figwidth, figheight = plt.rcParams['figure.figsize']
fig, axes = plt.subplots(1, 2, figsize=(2 * figwidth, figheight))

# with rio.open(img_filepath) as src:
with rio.open(image_to_predict) as src:
    plot.show(src.read(), ax=axes[0])
axes[1].set_title(image_to_predict)
axes[1].imshow(y_pred)
plt.show()
