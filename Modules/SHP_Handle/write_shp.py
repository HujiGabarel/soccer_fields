import matplotlib.pyplot as plt
import numpy as np
import shapefile
import cv2


def convert_row_col2coordinates(row, col, coordinates, km_radius, mask_size):
    """

    :param row:
    :param col:
    :param coordinates: coordinates of the center of the area
    :param km_radius:
    :param mask_size:
    :return: row and col in coordinates
    """
    m_radius = km_radius * 1000
    row_resolution, col_resolution = (m_radius * 2) / mask_size[0], (m_radius * 2) / mask_size[1]
    return (coordinates[0] - m_radius) + (col * col_resolution), (coordinates[1] + m_radius) - (row * row_resolution)


def convert_mask2polygons(image: np.ndarray, coordinates, km_radius) -> list:
    """
    convert the mask to polygons
    :param mask: mask
    :return: list of polygons
    """
    mask = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threshold = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for contour in contours:
        epsilon = 0.001 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        polygons.append(approx)

    polygon_coordinates = []
    for polygon in polygons:
        list_of_points_for_polygon = []
        for point in polygon:
            points_in_coordinates = convert_row_col2coordinates(point[0][0], point[0][1], coordinates, km_radius,
                                                                mask.shape)
            list_of_points_for_polygon.append(points_in_coordinates)
        polygon_coordinates.append(list_of_points_for_polygon)

    # Print the list of polygon coordinates
    for polygon in polygon_coordinates:
        print(polygon)
        print(1)

    return polygon_coordinates


def convert_mask2shp(mask: np.ndarray, directory_path: str):
    """
    convert the mask to shapefile and save it in the directory_path
    :param mask:
    :param directory_path:
    :return: none
    """
    list_of_polygons = convert_mask2polygons(mask)
    # Create a polygon shapefile writer
    return None


def draw_polygons_on_image(polygons: list):
    """
    draw polygons on image
    :param image: image
    :param polygons: list of polygons
    :return: image with polygons
    """
    # black image
    image = np.zeros((512, 512, 3), np.uint8)
    for polygon in polygons:
        pts = np.array(polygon, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], isClosed=True, color=(255, 255, 255), thickness=2)

    return image


if __name__ == '__main__':
    image = cv2.imread(
        "C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\Modules\\Main\\images_from_arcgis\\data_(698813, 3620547)\\mask_(698813, 3620547).png")

    list_of_polygons = convert_mask2polygons(image, (698813, 3620547), 0.3)
    new_image = draw_polygons_on_image(list_of_polygons)
    plt.imshow(new_image)
    plt.show()
