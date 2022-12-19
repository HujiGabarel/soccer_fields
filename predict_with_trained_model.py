from joblib import dump, load
import detectree as dtr
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio import plot
from os import path
"""
Load an image and a trained model, predict which pixels in the image are trees (yellow), and non trees (purple)
"""

trained_model_name = 'clf.joblib'
image_to_predict = "Forest Segmented/some_images_tif\\3484_sat_23.tif"

trained_model = load(trained_model_name)

#predict trees and non-trees
y_pred = dtr.Classifier().classify_img(image_to_predict, trained_model)

# side-by-side plot of the tile and the predicted tree/non-tree pixels
figwidth, figheight = plt.rcParams['figure.figsize']
fig, axes = plt.subplots(1, 2, figsize=(2 * figwidth, figheight))
with rio.open(image_to_predict) as src:
    plot.show(src.read(), ax=axes[0])
axes[1].imshow(y_pred)
plt.show()
