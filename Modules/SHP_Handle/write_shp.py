import matplotlib.pyplot as plt
import numpy as np
import shapefile
import cv2


def convert_point2coordinates(row, col, coordinates, km_radius, mask_size):
    """
    convert the point in the mask to coordinates values (from row and col to coordinates)
    :param row:
    :param col:
    :param coordinates: coordinates of the center of the area
    :param km_radius: radius in km
    :param mask_size: size of the mask
    :return: row and col in coordinates
    """
    m_radius = km_radius * 1000
    row_resolution, col_resolution = (m_radius * 2) / mask_size[0], (m_radius * 2) / mask_size[1]
    return (coordinates[0] - m_radius) + (col * col_resolution), (coordinates[1] + m_radius) - (row * row_resolution)


def create_polygons(image: np.ndarray, resolution=0.005) -> list:
    """
    create polygons from mask, each polygon is a list of points
    the function recognize the polygons by the contours of the mask and then approximate the contours
    finally, the function return the list of polygons
    :param resolution: this parameter is used to approximate the contours,
    the smaller the value, the more accurate the approximation
    :param image: the mask of the area, it is a binary image
    :return: list of polygons
    """
    mask = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threshold = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for contour in contours:
        epsilon = resolution * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        polygons.append(approx)
    return polygons


def convert_mask2polygons(mask: np.ndarray, coordinates, km_radius) -> list:
    """
    convert the mask to polygons in coordinates (each point is converted to coordinates)
    :param mask: mask
    :return: list of polygons in coordinates
    """
    polygons = create_polygons(mask)
    list_of_polygons = []
    for polygon in polygons:
        list_of_points_for_polygon = []
        for point in polygon:
            list_of_points_for_polygon.append(
                convert_point2coordinates(point[0][1], point[0][0], coordinates, km_radius, mask.shape))
        list_of_polygons.append(list_of_points_for_polygon)
    return list_of_polygons


def write_list_of_polygons_to_shp(list_of_polygons_in_coordinates: list, directory_path):
    """
    write the list of polygons to shapefile
    :param list_of_polygons:
    :param directory_path:
    :return:
    """
    shp = shapefile.Writer(directory_path+".shp", shapeType=shapefile.POLYGON)
    shp.field("ID", "N")
    for polygon in list_of_polygons_in_coordinates:
        print(polygon)
        shp.poly([polygon])
        shp.record(1)
    create_prj_file(directory_path)
    return None
def create_prj_file(directory_path):
    """
    create prj file for the shapefile
    :param directory_path:
    :return:
    """
    # Create the PRJ file
    prj = open("%s.prj" % directory_path, "w")
    epsg = 'PROJCS["WGS 84 / UTM zone 36N",'
    epsg += 'GEOGCS["WGS 84",DATUM["WGS_1984",'
    epsg += 'SPHEROID["WGS 84",6378137,298.257223563]],'
    epsg += 'PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],'
    epsg += 'PROJECTION["Transverse_Mercator"],'
    epsg += 'PARAMETER["latitude_of_origin",0],'
    epsg += 'PARAMETER["central_meridian",33],'
    epsg += 'PARAMETER["scale_factor",0.9996],'
    epsg += 'PARAMETER["false_easting",500000],'
    epsg += 'PARAMETER["false_northing",0],'
    epsg += 'UNIT["Meter",1]]'
    prj.write(epsg)
    prj.close()

def create_shp_file_of_mask(mask: np.ndarray, coordinates, km_radius, directory_path: str):
    """
    convert the mask to shapefile and save it in the directory_path
    :param mask:
    :param directory_path:
    :return: none
    """
    list_of_polygons = convert_mask2polygons(mask, coordinates, km_radius)
    shp_file_path = directory_path + f'\\mask_{coordinates[0], coordinates[1]}_{km_radius}'
    write_list_of_polygons_to_shp(list_of_polygons, shp_file_path)
    return None


if __name__ == '__main__':
    coordinates = (722796, 3652284)
    radius = 31.25
    # image_name = f'C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\Modules\\Main\\images_from_arcgis\\data_{coordinates[0], coordinates[1]}\\mask_{coordinates[0], coordinates[1]}.png'
    image_name="C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\Modules\\Main\\helicpoter_landing.jpg"
    image = cv2.imread(image_name)
    create_shp_file_of_mask(image, coordinates, radius,
                            f'C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\Modules\\Main')
    # create_shp_file_of_mask(image, coordinates, radius,
    #                         f'C:\\Users\\t8875796\\PycharmProjects\\soccer_field\\Modules\\Main\\images_from_arcgis\\data_{coordinates[0], coordinates[1]}')