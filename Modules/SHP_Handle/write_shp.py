import matplotlib.pyplot as plt
import numpy as np
import shapefile
import cv2


def convert_row_col_point2coordinates(row, col, coordinates, km_radius, mask_size):
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


def convert_row_col_list2coordinates_list(list_of_pol_rowcol, coordinates, km_radius, mask_size) -> list[list[tuple]]:
    """
    convert a list of polygons from row col to coordinates
    :param list_of_pol_rowcol:
    :param coordinates:
    :param km_radius:
    :param mask_size:
    :return:
    """
    list_of_polygons_in_cordinates = []
    for polygon in list_of_pol_rowcol:
        list_of_polygons_in_cordinates.append([])
        for point in polygon:
            points_in_coordinates = convert_row_col_point2coordinates(point[0], point[1], coordinates, km_radius,
                                                                      mask_size)
            # print(points_in_coordinates)
            list_of_polygons_in_cordinates[-1].append(points_in_coordinates)
    return list_of_polygons_in_cordinates


def create_polygons(image):
    """
    create polygons from mask
    :param image:
    :return:
    """
    mask = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threshold = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for contour in contours:
        epsilon = 0.005 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        polygons.append(approx)
    return polygons


def convert_mask2polygons(mask: np.ndarray) -> list:
    """
    convert the mask to polygons
    :param mask: mask
    :return: list of polygons
    """
    polygons = create_polygons(mask)
    list_of_polygons_in_row_colum = []
    for polygon in polygons:
        list_of_points_for_polygon = []
        for point in polygon:
            list_of_points_for_polygon.append((point[0][1], point[0][0]))
        list_of_polygons_in_row_colum.append(list_of_points_for_polygon)

    return list_of_polygons_in_row_colum


def write_list_of_polygons_to_shp(list_of_polygons_in_coordinates: list, directory_path):
    """
    write the list of polygons to shapefile
    :param list_of_polygons:
    :param directory_path:
    :return:
    """
    shp = shapefile.Writer(directory_path, shapeType=shapefile.POLYGON)
    shp.field("ID", "N")
    for polygon in list_of_polygons_in_coordinates:
        print(polygon)
        shp.poly([polygon])
        shp.record(1)

    return None


def create_shp_file_of_mask(mask: np.ndarray, coordinates, m_radius, directory_path: str):
    """
    convert the mask to shapefile and save it in the directory_path
    :param mask:
    :param directory_path:
    :return: none
    """
    list_of_polygons_in_row_colum = convert_mask2polygons(mask)
    list_of_polygons_in_coordinates = convert_row_col_list2coordinates_list(list_of_polygons_in_row_colum, coordinates,
                                                                            m_radius, mask.shape)
    shp_file_path = directory_path + f'\\mask_{coordinates[0], coordinates[1]}_{m_radius}.shp'
    write_list_of_polygons_to_shp(list_of_polygons_in_coordinates, shp_file_path)


# def draw_polygons_on_image(polygons: list, image_size):
#     """
#     Not in use, only for testing
#     draw polygons on black image
#     :param image: image
#     :param polygons: list of polygons
#     :return: image with polygons
#     """
#     image = np.zeros((image_size[0], image_size[1], 3), np.uint8)
#     for polygon in polygons:
#         pts = np.array(polygon, np.int32)
#         pts = pts.reshape((-1, 1, 2))  # reshape to 2D points
#         cv2.polylines(image, [pts], isClosed=True, color=(255, 255, 255), thickness=2)  # draw the polygon
#
#     return image


if __name__ == '__main__':
    coordinates = (698813, 3620547)
    radius = 0.3
    image_name = f'C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\Modules\\Main\\images_from_arcgis\\data_{coordinates[0], coordinates[1]}\\mask_{coordinates[0], coordinates[1]}.png'
    image = cv2.imread(image_name)
    create_shp_file_of_mask(image, coordinates, radius, f'C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\Modules\\Main\\images_from_arcgis\\data_{coordinates[0], coordinates[1]}')
    list_of_polygons_in_row_colum = convert_mask2polygons(image)
    new_image = draw_polygons_on_image(list_of_polygons_in_row_colum, image.shape)
    plt.imshow(new_image)
    plt.show()
    # list_of_polygons_in_coordinates = convert_row_col_list2coordinates_list(list_of_polygons_in_row_colum, coordinates,
    #                                                                         radius, image.shape)
    # write_list_of_polygons_to_shp(list_of_polygons_in_coordinates)
