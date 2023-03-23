import matplotlib.pyplot as plt
import numpy as np
from Modules.Slopes.slopes import get_max_height_differences, plot_heat_map
import rasterio


def get_image_from_utm(coordinates):
    # Returns an image from the coordinates with the SIZE * SIZE size
    pass


def get_tree_mask_from_image(aerial):
    # using trees module, get the mask of the trees in black white
    pass


def get_partial_dtm_from_utm(coordinates, SIZE, meters_per_pixel):
    # find the area in the dtm that is relevant
    # cut around the area in a SIZE*SIZE matrix

    file_path = "../../some.tif"
    dem = rasterio.open(file_path)
    rows = dem.height
    cols = dem.width
    dem_data = dem.read(1).astype("float64")
    print(dem_data)

    ### assuming that the coordinates[0] is cols (easting) and coordinates[1] is rows (northing)
    row_center = round((coordinates[1] - dem.bounds.bottom) / meters_per_pixel)
    col_center = round((coordinates[0] - dem.bounds.left) / meters_per_pixel)
    print(row_center, col_center)

    sub_matrix = dem_data[row_center - SIZE: row_center + SIZE, col_center - SIZE: col_center + SIZE]
    print(sub_matrix)
    new_rows = sub_matrix.shape[0]
    new_cols = sub_matrix.shape[1]
    partial_max_height_diff = get_max_height_differences(sub_matrix, new_rows, new_cols)

    return partial_max_height_diff, new_rows, new_cols


def get_total_mask_from_masks(tree_mask, heights_mask):
    # return tree_mask * heights_mask
    tree_mask_np=np.array(tree_mask)
    heights_mask_np=np.array(heights_mask)
    return np.multiply(tree_mask_np,heights_mask_np)


def get_slopes_mask_from_dtm(dtm):
    # get heights from the dtm
    # get slopes from the heights
    # get mask from the slopes
    # return mask
    #TODO: SIZE of the image is constant?
    pass


def get_viable_landing_in_radius(coordinates, radius = 1):
    # LOOP OVER ALL THE COORDINATES IN THE RADIUS
    #     aerial = get_image_from_utm(coordinates)
    #     tree_mask = get_tree_mask_from_image(aerial)
    #     dtm = get_partial_dtm_from_utm(coordinates)
    #     heights_mask = get_slopes_mask_from_dtm(dtm)
    #     total_mask = get_total_mask_from_masks(tree_mask, heights_mask)
    #     plt.imshow(total_mask)
    pass


def main():
    """coordinates = (0, 0)
    get_viable_landing_in_radius(coordinates)"""
    coordinates = (684825.0, 3621765.0)
    SIZE = 10
    meters_per_pixel = 10
    partial_max_height_diff, new_rows, new_cols = get_partial_dtm_from_utm(coordinates, SIZE, meters_per_pixel)
    plot_heat_map(partial_max_height_diff, 10, new_rows, new_cols)


if __name__ == '__main__':
    main()

