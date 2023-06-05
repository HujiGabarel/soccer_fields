import shapefile
from PIL import Image, ImageDraw
import numpy as np
import cv2
import matplotlib.pyplot as plt

# opening the vector map
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
    :return: box of shape (x_min, y_min, x_max, y_max), one box for one shape
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
    :return: True if one vertex (or more) of the box is in the area, else False
    """
    min_x, min_y = box[0], box[1]
    max_x, max_y = box[2], box[3]
    radius_in_km = radius * 1000
    if (coordinates[0] - radius_in_km < min_x < coordinates[0] + radius_in_km) and (
            coordinates[1] - radius_in_km < min_y < coordinates[1] + radius_in_km) or (
            (coordinates[0] - radius_in_km < max_x < coordinates[0] + radius_in_km) and (
            coordinates[1] - radius_in_km < max_y < coordinates[1] + radius_in_km)) or (
            (coordinates[0] - radius_in_km < min_x < coordinates[0] + radius_in_km) and (
            coordinates[1] - radius_in_km < max_y < coordinates[1] + radius_in_km)) or (
            (coordinates[0] - radius_in_km < max_x < coordinates[0] + radius_in_km) and (
            coordinates[1] - radius_in_km < min_y < coordinates[1] + radius_in_km)
    ):
        return radius_in_km
    return False


def calculate_total_box(list_of_shapes, coordinates, radius_in_km):
    if len(list_of_shapes) == 0:
        print("No shapes in the area")
        return None
    radius = radius_in_km * 1000
    x_min, y_min, x_max, y_max = coordinates[0] - radius, coordinates[1] - radius, coordinates[0] + radius, \
                                 coordinates[1] + radius
    x, y = [int(x_min), int(x_max)], [int(y_min), int(y_max)]
    for shape in list_of_shapes:
        box = shape[1]
        x.append(int(box[0]))  # x_min
        x.append(int(box[2]))  # x_max
        y.append(int(box[1]))  # y_min
        y.append(int(box[3]))  # y_max
    total_box = min(x), min(y), max(x), max(y)
    return total_box


def create_mask_from_shapes(box_of_shapes_in_the_area, shapes_in_the_area):
    """
    :param shape: shapefile shape
    :return: mask of the shape
    """

    image_width = int(box_of_shapes_in_the_area[2] - box_of_shapes_in_the_area[0])
    image_height = int(box_of_shapes_in_the_area[3] - box_of_shapes_in_the_area[1])
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)
    for shape in shapes_in_the_area:
        relative_list_of_points = create_relative_points(shape[0], box_of_shapes_in_the_area)
        draw.polygon(relative_list_of_points, outline=UNVIABLE_LANDING, fill=UNVIABLE_LANDING)

    return convert_image_to_mask(image)


def convert_image_to_mask(image):  # Todo: improve this
    mask = np.array(image)
    mask = mask.sum(axis=2)
    mask[mask == 0] = UNVIABLE_LANDING
    mask[mask == 765] = VIABLE_LANDING
    return mask


def create_relative_points(list_of_points, box_of_shapes_in_the_area):
    """

    :param list_of_points:
    :param box_of_shapes_in_the_area:
    :return:
    """
    new_list_of_points = []
    for point in list_of_points:
        # relative to the top left corner
        new_point = (point[0] - box_of_shapes_in_the_area[0], -point[1] + box_of_shapes_in_the_area[3])
        new_list_of_points.append(new_point)
    return new_list_of_points


def change_resolution_of_mask(mask, image_size):
    """
    :param mask:  mask
    :param image_size: the new size of the mask
    :return:
    """
    mask = mask.astype(np.uint8)
    mask = cv2.resize(mask, image_size, interpolation=cv2.INTER_NEAREST)
    return mask


def create_box(coordinates, m_radius):
    """
    get the coordinates of the center of the area and the radius and return the box of the area
    :param coordinates: coordinates of the center of the area
    :param m_radius: radius in meters
    :return: box of the area
    """
    return (coordinates[0] - m_radius, coordinates[1] - m_radius, coordinates[0] + m_radius, coordinates[1] + m_radius)


def calculate_top_left(original_area_box, total_box, row_resolution, col_resolution):
    """
    calculate the top left point of the original area in the total box
    :param original_area_box:
    :param total_box:
    :param row_resolution:
    :param col_resolution:
    :return:
    """
    top_left_row = -int((original_area_box[3] - total_box[3]) / row_resolution)
    top_left_col = int((original_area_box[0] - total_box[0]) / col_resolution)
    return top_left_row, top_left_col


def calculate_right_bottom(original_area_box, total_box, row_resolution, col_resolution):
    """
    calculate the bottom right point of the original area in the total box
    :param original_area_box:
    :param total_box:
    :param row_resolution:
    :param col_resolution:
    :return:
    """
    bottom_right_row = -int((original_area_box[1] - total_box[3]) / row_resolution)
    bottom_right_col = int((original_area_box[2] - total_box[0]) / col_resolution)
    return bottom_right_row, bottom_right_col


def get_partial_mask_from_total_mask(total_mask_from_shape, total_box, coordinates, radius):
    """
    :param total_mask_from_shape: mask of the total area
    :param coordinates: coordinates of the center of the area
    :param radius: radius in km
    :return: mask in box of the relevant area
    """
    m_radius = radius * 1000
    original_area_box = create_box(coordinates, m_radius)
    row_resolution, col_resolution = (total_box[3] - total_box[1]) / total_mask_from_shape.shape[0] \
        , (total_box[2] - total_box[0]) / total_mask_from_shape.shape[1]
    top_left_row, top_left_col = calculate_top_left(original_area_box, total_box, row_resolution, col_resolution)
    bottom_right_row, bottom_right_col = calculate_right_bottom(original_area_box, total_box, row_resolution,
                                                                col_resolution)
    partial_mask = total_mask_from_shape[top_left_row:bottom_right_row, top_left_col:bottom_right_col]
    return partial_mask


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
    box_of_shapes_in_the_area = calculate_total_box(shapes_in_the_area, coordinates, radius)
    if box_of_shapes_in_the_area is None:
        return np.ones(image_size) * VIABLE_LANDING
    mask = create_mask_from_shapes(box_of_shapes_in_the_area, shapes_in_the_area)
    partial_mask = get_partial_mask_from_total_mask(mask, box_of_shapes_in_the_area, coordinates, radius)
    mask_for_area = change_resolution_of_mask(partial_mask, image_size)
    return mask_for_area


if __name__ == '__main__':

    coordinates = (698813, 3620547)
    radius_in_km = 0.3
    mask=get_mask_from_shp_file(SHP_PATH, coordinates, radius_in_km, (400, 400))
    plt.imshow(mask)
    plt.show()
