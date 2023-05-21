import shapefile
import os

# opening the vector map
SHP_PATH = "../../SHP_UTM/B_SITES_A.shp"


def shp_file_to_list_of_shapes() -> list[tuple[list[tuple[float, float]], tuple[float, float, float, float]]]:
    with shapefile.Reader(SHP_PATH) as shp:
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
    :param box:
    :param coordinates: the center of the area
    :param km_radius:
    :return:
    """
    min_x,min_y = box[0],box[1]
    max_x,max_y = box[2],box[3]
    radius_in_km = radius * 1000
    if (coordinates[0] - radius_in_km < min_x and coordinates[0] + radius_in_km > max_x) and (
            coordinates[1] - radius_in_km < min_y and coordinates[1] + radius_in_km > max_y):
        return radius_in_km
    return False


if __name__ == '__main__':
    print(len(get_shapes_in_the_area((696531, 3662682), 7, shp_file_to_list_of_shapes())))
