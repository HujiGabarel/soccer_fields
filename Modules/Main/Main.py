import matplotlib.pyplot as plt
import numpy as np
import os
import json
import image_downloading
import rasterio
import cv2
import rasterio as rio
from rasterio import plot
from Modules.Trees.predict_with_trained_model import predict_image
from Modules.Slopes.slopes import get_max_slopes, plot_heat_map, convert_slopes_to_black_and_white
from Modules.GUI import gui
import Area_filter

DTM_FILE_PATH = "../../DTM_data/top.tif"
trained_model_path = "../../Models/our_models/official_masks_10%.joblib"  # The trained model


# TODO: decide about length
def get_image_from_utm(coordinates, km_radius):
    """

    Args:
        coordinates (_type_): _description_
    """

    with open("preferences.json", 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    lat, long = image_downloading.convert_to_lat_long(coordinates)
    img = image_downloading.download_image(lat, long, prefs["zoom"], prefs['url'], prefs['tile_size'],
                                           length=2 * km_radius)

    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'images_from_argcis/img_{coordinates[0], coordinates[1]}.png'
    cv2.imwrite(name, img)
    print(f'Saved as {name}')
    return name, img


def get_tree_mask_from_image(aerial, trained_model_path):
    # using trees module, get the mask of the trees in black white
    return predict_image(aerial, trained_model_path)


def cheack_coordinates_area_are_in_dtm(coordinates, size, dem):
    return ((dem.bounds.left < (coordinates[0] + size) < dem.bounds.right) and
            (dem.bounds.left < (coordinates[0] - size) < dem.bounds.right) and
            (dem.bounds.bottom < (coordinates[1] + size) < dem.bounds.top) and
            (dem.bounds.bottom < (coordinates[1] - size) < dem.bounds.top)
            )


def get_partial_dtm_from_total_dtm(coordinates, km_radius, meters_per_pixel=10):
    # find the area in the dtm that is relevant
    # cut around the area in a SIZE*SIZE matrix
    size = round(km_radius * 1000 / meters_per_pixel)
    dem = rasterio.open(DTM_FILE_PATH)  # turn .tiff file to dem format, each pixel is a height
    rows = dem.height  # number of rows
    cols = dem.width  # number of columns
    dem_data = dem.read(1).astype("int")  # convert height to int instead of float

    ### assuming that the coordinates[0] is cols (east / west) and coordinates[1] is rows (north / south)

    # calculating the center for partial_dtm
    if cheack_coordinates_area_are_in_dtm(coordinates, size, dem):
        print("coordinates are in range")
    print(dem.bounds.left, dem.bounds.top)
    col_center = round((coordinates[0] - dem.bounds.left) / meters_per_pixel)
    row_center = -round((coordinates[1] - dem.bounds.top) / meters_per_pixel)
    partial_dtm = dem_data[row_center - size: row_center + size, col_center - size: col_center + size]
    new_rows = partial_dtm.shape[0]
    new_cols = partial_dtm.shape[1]

    return partial_dtm, new_rows, new_cols


def get_w_or_b(e, n, e_center, n_center, m_radius, trees, slopes):
    row_tree = round((n - n_center + m_radius) / (2 * m_radius) * trees.shape[0])
    col_tree = round((e - e_center + m_radius) / (2 * m_radius) * trees.shape[1])
    row_slope = round((n - n_center + m_radius) / (2 * m_radius) * slopes.shape[0]) - 1
    col_slope = round((e - e_center + m_radius) / (2 * m_radius) * slopes.shape[1]) - 1
    tree = trees[row_tree][col_tree]
    slope = slopes[row_slope][col_slope]
    # what white is 0??? yes so its need to be
    return tree or slope


def get_total_mask_from_masks(e_center, n_center, radius, trees, slopes):  # radius??? diffrent
    # return tree_mask * heights_mask
    total_mask = []
    m_radius = int(radius * 1000)
    for row, n in enumerate(range((n_center - m_radius), (n_center + m_radius))):
        total_mask.append([])
        for col, e in enumerate(range((e_center - m_radius), (e_center + m_radius))):
            total_mask[row].append(get_w_or_b(e, n, e_center, n_center, m_radius, trees, slopes))
    return np.array(total_mask)


def plot_image_and_mask(image_to_predict, predicted_mask_tree, predicted_mask_slope, total_mask, coordinates):
    # This part is only plotting style:
    # plots predicted and original images
    # side-by-side plot of the tile and the masks
    fig, axes = plt.subplots(2, 2)
    # with rio.open(img_filepath) as src:
    with rio.open(image_to_predict) as src:
        plot.show(src.read(), ax=axes[0][0])
    axes[0][0].set_title("Image: " + str(coordinates))
    axes[1][0].set_title("tree mask")
    axes[1][0].imshow(predicted_mask_tree, cmap='Greys', interpolation='nearest')
    axes[1][1].set_title("slopes mask")
    axes[1][1].imshow(predicted_mask_slope, cmap='Greys', interpolation='nearest')
    axes[0][1].set_title("total mask")
    axes[0][1].imshow(total_mask, cmap='Greys', interpolation='nearest')
    saved_image_name = str(int(coordinates[0])) + "," + str(int(coordinates[1])) + " RESULT"
    plt.savefig(os.path.join("results_images", saved_image_name))
    plt.show()


def get_viable_landing_in_radius(coordinates, km_radius):
    image_name, img = get_image_from_utm(coordinates, km_radius)
    partial_dtm, new_rows, new_cols = get_partial_dtm_from_total_dtm(coordinates, km_radius)
    slopes_mask = get_max_slopes(partial_dtm, new_rows, new_cols)
    slopes_mask_in_black_and_white = np.array(convert_slopes_to_black_and_white(slopes_mask, new_rows, new_cols))
    # plot_heat_map(slopes_mask_in_black_and_white)
    # slopes_mask_after_area_filter = Area_filter.find_fields(slopes_mask_in_black_and_white, 20, 20, 0, 255)[1]
    # This work with image name only when image is in Main dir, else need full path!
    tree_mask = get_tree_mask_from_image(image_name, trained_model_path)

    total_mask = get_total_mask_from_masks(coordinates[0], coordinates[1], km_radius, tree_mask,
                                           slopes_mask_in_black_and_white)

    # plot_image_and_mask(image_name, tree_mask, slopes_mask_in_black_and_white,
    #                     total_mask, coordinates)

    return img, total_mask


if __name__ == '__main__':
    # BoundingBox(left=692125.0, bottom=3614785.0, right=705335.0, top=3623875.0) Yokneam
    # BoundingBox(left=684825.0, bottom=3621765.0, right=689175.0, top=3624175.0) some
    # BoundingBox(left=666735.0, bottom=3590995.0, right=852765.0, top=3823815.0) top
    screen = gui.GUI()
    screen.mainloop()
    # coordinates = (690096, 3630643, 36, 'N')
    # 698342,3618731
    # km_radius = 0.1
    # get_viable_landing_in_radius(coordinates, km_radius)
