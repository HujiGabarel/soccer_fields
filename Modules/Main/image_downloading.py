import cv2
import requests
import numpy as np
import threading
import geopy.distance
import utm

def download_tile(url, channels):
    """

    :param url: url of img
    :param channels: num of channels in img format
    :return: image
    """
    response = requests.get(url)
    arr = np.asarray(bytearray(response.content), dtype=np.uint8)
    
    if channels == 3:
        return cv2.imdecode(arr, 1)
    return cv2.imdecode(arr, -1)


def convert_to_lat_long(utm_value):
    """
    convert from utm to lat long
    :param utm_value: addressed as dict
    :return: coordinates in (latitude,longitude)
    """

    cords = utm.to_latlon(*utm_value)
    return cords

def get_square_edges_from_center(lat, long, length):
    """
    
    :param lat: lattitude of square center
    :param long:  Longitude of sqaure center
    :param length: side of squre in [km]

    :return: coordinates in (latitude,longitude)
    """
    lat_tl,long_tl,_ = geopy.distance.distance(kilometers=length/2).destination((lat,long),bearing=-90)
    lat_tl,long_tl,_ = geopy.distance.distance(kilometers=length/2).destination((lat_tl,long_tl),bearing=0)


    lat_br,long_br,_ = geopy.distance.distance(kilometers=length/2).destination((lat,long),bearing=90)
    lat_br,long_br,_ = geopy.distance.distance(kilometers=length/2).destination((lat_br,long_br),bearing=180)

    return (lat_tl,long_tl),(lat_br,long_br)   


# Mercator projection 
# https://developers.google.com/maps/documentation/javascript/examples/map-coordinates
def project_with_scale(lat, lon, scale):
    """

    :param lat: latitude 
    :param lon: Longitude 
    :param scale: scale of img (according to zoom)
    :return: coordinates
    """
    siny = np.sin(lat * np.pi / 180)
    siny = min(max(siny, -0.9999), 0.9999)
    x = scale * (0.5 + lon / 360)
    y = scale * (0.5 - np.log((1 + siny) / (1 - siny)) / (4 * np.pi))
    return x, y


def download_image(lat_center,long_center, zoom, url, tile_size = 256, channels = 3,length=10):
    """

    :param lat_center: latitude of img center
    :param long_center: long of img center
    :param zoom: _description_
    :param url: _description_
    :param tile_size: _description_, defaults to 256
    :param channels: _description_, defaults to 3
    :param length: _description_, defaults to 10
    :return: _description_
    """

    (lat_tl,long_tl), (lat_br,long_br) = get_square_edges_from_center(lat_center, long_center,length)


    scale = 1 <<zoom

    # Find the pixel coordinates and tile coordinates of the corners
    tl_proj_x, tl_proj_y = project_with_scale(lat_tl, long_tl, scale)
    br_proj_x, br_proj_y = project_with_scale(lat_br, long_br, scale)

    tl_pixel_x = int(tl_proj_x * tile_size)
    tl_pixel_y = int(tl_proj_y * tile_size)
    br_pixel_x = int(br_proj_x * tile_size)
    br_pixel_y = int(br_proj_y * tile_size)

    tl_tile_x = int(tl_proj_x)
    tl_tile_y = int(tl_proj_y)
    br_tile_x = int(br_proj_x)
    br_tile_y = int(br_proj_y)
    img_w = abs(tl_pixel_x - br_pixel_x)
    img_h = br_pixel_y - tl_pixel_y
    img = np.ndarray((img_h, img_w, channels), np.uint8)

    def build_row(row_number):
        for j in range(tl_tile_x, br_tile_x + 1):
            tile = download_tile(url.format(x=j, y=row_number, z=zoom), channels)

            # Find the pixel coordinates of the new tile relative to the image
            tl_rel_x = j * tile_size - tl_pixel_x
            tl_rel_y = row_number * tile_size - tl_pixel_y
            br_rel_x = tl_rel_x + tile_size
            br_rel_y = tl_rel_y + tile_size

            # Define where the tile will be placed on the image
            i_x_l = max(0, tl_rel_x)
            i_x_r = min(img_w + 1, br_rel_x)
            i_y_l = max(0, tl_rel_y)
            i_y_r = min(img_h + 1, br_rel_y)

            # Define how border tiles are cropped
            cr_x_l = max(0, -tl_rel_x)
            cr_x_r = tile_size + min(0, img_w - br_rel_x)
            cr_y_l = max(0, -tl_rel_y)
            cr_y_r = tile_size + min(0, img_h - br_rel_y)

            img[i_y_l:i_y_r, i_x_l:i_x_r] = tile[cr_y_l:cr_y_r, cr_x_l:cr_x_r]

    threads = []
    for i in range(tl_tile_y, br_tile_y + 1):
        thread = threading.Thread(target=build_row, args=[i])
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    return img


def image_size(lat1, lon1, lat2, lon2, zoom, tile_size = 256):
    """_summary_

    :param lat1: lat of top-left
    :param lon1: lon of top-left
    :param lat2: lat of bottom-right
    :param lon2: lon of bottom_rigth
    :param zoom: _description_
    :param tile_size: size of tile, defaults to 256
    :return: size of frull image
    """

    scale = 1<<int(zoom)
    tl_proj_x, tl_proj_y = project_with_scale(lat1, lon1, scale)
    br_proj_x, br_proj_y = project_with_scale(lat2, lon2, scale)

    tl_pixel_x = int(tl_proj_x * tile_size)
    tl_pixel_y = int(tl_proj_y * tile_size)
    br_pixel_x = int(br_proj_x * tile_size)
    br_pixel_y = int(br_proj_y * tile_size)

    return abs(tl_pixel_x - br_pixel_x), br_pixel_y - tl_pixel_y
