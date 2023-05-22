import shapefile
from PIL import Image, ImageDraw
import numpy as np
from skimage import color
import matplotlib.pyplot as plt
import cv2

# opening the vector map
SHP_PATH = "../../SHP_UTM/B_SITES_A.shp"
from Modules.GUI.settings import *


def shp_file_to_list_of_shapes(shp_path) -> list[tuple[list[tuple[float, float]], tuple[float, float, float, float]]]:
    """

    :param shp_path: shp file path
    :return: list of shapes that each shape is a tuple of list of points and box of the shape
    shape[0] = list of points, shape[1] = box of the shape
    """
    with shapefile.Reader(shp_path) as shp:
        print(shp)
        shapes = shp.shapes()
        shapes_list = []
        for shape_number in range(len(shapes)):
            list_of_points = shapes[shape_number].points
            shapes_list.append((list_of_points, calculate_box_of_shape(list_of_points)))
    return shapes_list


def calculate_box_of_shape(list_of_points):
    """
    :param shape: shapefile shape
    :return: box of shape
    """
    x, y = [], []
    for point in list_of_points:
        x.append(point[0])
        y.append(point[1])
    return min(x), min(y), max(x), max(y)


def get_shapes_in_the_area(cordinates, km_radius, shapes_list):
    """
    :param cordinates: tuple of cordinates (x,y)
    :param km_radius: radius in km
    :param shapes_list: list of shapes
    :return: list of shapes in the area
    """
    shapes_in_the_area = []
    for shape in shapes_list:
        if is_box_in_the_area(shape[1], cordinates, km_radius):
            shapes_in_the_area.append(shape)
    return shapes_in_the_area


def is_box_in_the_area(box, coordinates, radius):
    """
    :param box: box of the shape
    :param coordinates: the center of the area
    :param km_radius: radius in km (from the user)
    :return: True if the box is in the area, else False
    """
    min_x, min_y = box[0], box[1]
    max_x, max_y = box[2], box[3]
    radius_in_km = radius * 1000
    if (coordinates[0] - radius_in_km < min_x and coordinates[0] + radius_in_km > max_x) and (
            coordinates[1] - radius_in_km < min_y and coordinates[1] + radius_in_km > max_y):
        return radius_in_km
    return False


def calculate_box_of_shapes_in_the_area(list_of_shapes):
    if len(list_of_shapes) == 0:
        print("No shapes in the area")
        return None
    x, y = [], []
    for shape in list_of_shapes:
        box = shape[1]
        x.append(box[0])  # x_min
        x.append(box[2])  # x_max
        y.append(box[1])  # y_min
        y.append(box[3])  # y_max

    return min(x), min(y), max(x), max(y)


def create_mask_from_shapes(box_of_shapes_in_the_area, shapes_in_the_area):
    """
    :param shape: shapefile shape
    :return: mask of the shape
    """

    # Define the size of the image
    image_width = int(box_of_shapes_in_the_area[2] - box_of_shapes_in_the_area[0])
    image_height = int(box_of_shapes_in_the_area[3] - box_of_shapes_in_the_area[1])
    # Create a blank image with a white background
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)
    for shape in shapes_in_the_area:
        relative_list_of_points = create_relative_points(shape[0], box_of_shapes_in_the_area)
        draw.polygon(relative_list_of_points, outline=UNVIABLE_LANDING, fill=UNVIABLE_LANDING)
    image.show()

    return convert_image_to_mask(image)


def convert_image_to_mask(image):  # Todo: improve this
    mask = np.array(image)
    mask = mask.sum(axis=2)
    mask[mask == 0] = UNVIABLE_LANDING
    mask[mask == 765] = VIABLE_LANDING
    return mask


def create_relative_points(list_of_points, box_of_shapes_in_the_area):
    new_list_of_points = []
    for point in list_of_points:
        # relative to the top left corner
        new_point = (point[0] - box_of_shapes_in_the_area[0], -point[1] + box_of_shapes_in_the_area[3])
        new_list_of_points.append(new_point)
    return new_list_of_points


def change_resolution_of_mask(mask, image_size):
    """
    :param mask: mask of the shape
    :param resolution: resolution of the mask
    :return: mask with the given resolution
    """
    # resize the mask to the size of the image
    mask = mask.astype(np.uint8)
    print(mask.shape)
    mask = cv2.resize(mask, image_size, interpolation=cv2.INTER_NEAREST)
    return mask


def get_partial_mask_from_total_mask(total_mask_from_shape, box_of_shapes_in_the_area, coordinates, radius,
                                     image_size: tuple):
    """
    # Todo: fix this
    :param total_mask_from_shape:
    :param coordinates:
    :param radius:
    :return: mask in box of the relevant area
    """
    km_radius = radius * 1000
    original_area_box = (
        coordinates[0] - km_radius, coordinates[1] - km_radius, coordinates[0] + km_radius, coordinates[1] + km_radius)
    print(original_area_box, box_of_shapes_in_the_area)
    row_resolution = (box_of_shapes_in_the_area[3] - box_of_shapes_in_the_area[1]) / total_mask_from_shape.shape[
        0]  # meter per pixel
    col_resolution = (box_of_shapes_in_the_area[2] - box_of_shapes_in_the_area[0]) / total_mask_from_shape.shape[
        1]  # meter per pixel
    print(row_resolution, col_resolution)

    partial_mask = 0  # Todo find the relevant part of the mask
    resized_mask_in_area = change_resolution_of_mask(partial_mask, image_size)
    plt.imshow(resized_mask_in_area)
    plt.show()

    return resized_mask_in_area


def get_mask_from_shp_file(shp_path, coordinates, radius, image_size: tuple):
    """
    :param shp_path: shp file path
    :param coordinates: coordinates of the area
    :param radius: radius of the area
    :param image_size: size of the image in pixels (width, height)
    :return: mask of the area
    """
    shapes_list = shp_file_to_list_of_shapes(shp_path)
    shapes_in_the_area = get_shapes_in_the_area(coordinates, radius, shapes_list)
    box_of_shapes_in_the_area = calculate_box_of_shapes_in_the_area(shapes_in_the_area)
    mask = create_mask_from_shapes(box_of_shapes_in_the_area, shapes_in_the_area)
    mask_for_area = get_partial_mask_from_total_mask(mask, box_of_shapes_in_the_area, coordinates, radius,
                                                     image_size)  # TODO: finish this
    return mask_for_area


if __name__ == '__main__':
    coordinates = (696531, 3662682)
    radius_in_km = 1

    # print(len(get_shapes_in_the_area(coordinates, radius_in_km, shp_file_to_list_of_shapes(SHP_PATH))))
    # list_of_shp = shp_file_to_list_of_shapes(SHP_PATH)
    # list_of_shp_in_the_area = get_shapes_in_the_area(coordinates, radius_in_km, list_of_shp)
    # box_of_shapes_in_the_area = calculate_box_of_shapes_in_the_area(list_of_shp_in_the_area)
    # total_mask_from_shape = create_mask_from_shapes(box_of_shapes_in_the_area, list_of_shp_in_the_area)
    # new_mask = change_resolution_of_mask(total_mask_from_shape, 10)
    # print(len(new_mask), len(new_mask[0]))
    get_mask_from_shp_file(SHP_PATH, coordinates, radius_in_km, (400, 400))
