import os
import sys
import time
import traceback
from typing import Union, Tuple, Any

import numpy as np
import cv2
from torch import Tensor

from building_footprint_segmentation.utils.date_time import get_time
from building_footprint_segmentation.utils.py_network import convert_tensor_to_numpy

from math import ceil,floor
def handle_dictionary(input_dictionary: dict, key: Any, value: Any) -> dict:
    """

    :param input_dictionary:
    :param key:
    :param value:
    :return:
    """
    if key not in input_dictionary:
        input_dictionary[key] = value
    elif type(input_dictionary[key]) == list:
        input_dictionary[key].append(value)
    else:
        input_dictionary[key] = [input_dictionary[key], value]

    return input_dictionary


def dict_to_string(input_dict: dict, separator=", ") -> str:
    """

    :param input_dict:
    :param separator:
    :return:
    """
    combined_list = list()
    for key, value in input_dict.items():
        individual = "{} : {:.5f}".format(key, value)
        combined_list.append(individual)
    return separator.join(combined_list)


def make_directory(current_dir: str, folder_name: str) -> str:
    """

    :param current_dir:
    :param folder_name:
    :return:
    """
    new_dir = os.path.join(current_dir, folder_name)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    return new_dir


def is_overridden_func(func):
    # https://stackoverflow.com/questions/9436681/how-to-detect-method-overloading-in-subclasses-in-python
    obj = func.__self__
    base_class = getattr(super(type(obj), obj), func.__name__)
    return func.__func__ != base_class.__func__


def extract_detail():
    """Extracts failing function name from Traceback
    by Alex Martelli
    http://stackoverflow.com/questions/2380073/how-to-identify-what-function-call-raise-an-exception-in-python
    """
    tb = sys.exc_info()[-1]
    stk = traceback.extract_tb(tb, -1)[0]
    return "{} in {} line num {} on line {} ".format(
        stk.name, stk.filename, stk.lineno, stk.line
    )


def get_details(fn):
    class_name = vars(sys.modules[fn.__module__])[
        fn.__qualname__.split(".")[0]
    ].__name__
    fn_name = fn.__name__
    if class_name == fn_name:
        return None, fn_name
    else:
        return class_name, fn_name


def crop_image(
    input_image: np.ndarray, crop_to_dimension: tuple, random_coord: tuple
) -> np.ndarray:
    """

    :param input_image:
    :param crop_to_dimension:
    :param random_coord:
    :return:
    """
    model_height, model_width = crop_to_dimension
    height, width = random_coord

    input_image = input_image[
        height : height + model_height, width : width + model_width
    ]

    return input_image


def get_random_crop_x_and_y(
    crop_to_dimension: tuple, base_dimension: tuple
) -> Tuple[int, int]:
    """

    :param crop_to_dimension:
    :param base_dimension:
    :return:
    """
    crop_height, crop_width = crop_to_dimension
    base_height, base_width = base_dimension
    h_start = np.random.randint(0, base_height - crop_height)
    w_start = np.random.randint(0, base_width - crop_height)

    return h_start, w_start


def get_pad_limit(model_input_dimension: tuple, image_input_dimension: tuple) -> int:
    """

    :param model_input_dimension:
    :param image_input_dimension:
    :return:
    """
    model_height, model_width = model_input_dimension
    image_height, image_width = image_input_dimension

    limit = (model_height - image_height) // 2
    return limit


def pad_image(img: np.ndarray, limit: int) -> np.ndarray:
    """

    :param img:
    :param limit:
    :return:
    """
    img = cv2.copyMakeBorder(
        img, limit, limit, limit, limit, borderType=cv2.BORDER_REFLECT_101
    )
    return img


def perform_scale(
    img: np.ndarray, dimension: tuple, interpolation=cv2.INTER_NEAREST
) -> np.ndarray:
    """

    :param img:
    :param dimension:
    :param interpolation:
    :return:
    """
    new_height, new_width = dimension
    img = cv2.resize(img, (new_width, new_height), interpolation=interpolation)
    return img


def load_image(path: str):
    """

    :param path:
    :return:
    """
    img = cv2.imread(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def to_binary(
    prediction: Union[np.ndarray, Tensor], cutoff=0.40
) -> Union[np.ndarray, Tensor]:
    """

    :param prediction:
    :param cutoff:
    :return:
    """
    prediction[prediction >= cutoff] = 1
    prediction[prediction < cutoff] = 0
    return prediction


def get_numpy(data: Union[Tensor, np.ndarray]) -> np.ndarray:
    """

    :param data:
    :return:
    """
    return convert_tensor_to_numpy(data) if type(data) == Tensor else data


def compute_eta(start, current_iter, total_iter):
    """

    :param start:
    :param current_iter:
    :param total_iter:
    :return:
    """
    e = time.time() - start
    eta = e * total_iter / current_iter - e
    return get_time(eta)

def slice_and_pad_array(img, tl, br,dim):

    # Slice the array
    y1,x1 = tl
    y2,x2 = br
    
    img_shape = img.shape

    actual_x2 = img.shape[1] if x2 > img_shape[1] else x2
    actual_y2 = img.shape[0] if y2 > img_shape[0] else y2

    
    actual_x1 = actual_x2 - dim[1] 
    actual_y1 = actual_y2 - dim[0]

    #check if image is too big
    pad_x = max(0,-actual_x1)
    pad_y = max(0,-actual_y1)

    actual_x1 = max(actual_x1,0)
    actual_y1 = max(actual_y1,0)

    sliced_arr = img[actual_y1:actual_y2, actual_x1:actual_x2,:]

    #make padding if not enough data is available
    final_arr = np.pad(sliced_arr, ((0, pad_y), (0, pad_x),(0,0)), mode='constant')


    
    shape = (actual_y2 - y1, actual_x2 - x1)
    start_x,end_x = x1-actual_x1, actual_x2-actual_x1
    start_y,end_y = y1-actual_y1, actual_y2-actual_y1
    return final_arr,(shape,(start_x,end_x),(start_y,end_y))
    
    # Compute the current size of the sliced array
    current_size = sliced_arr.shape
    
    # Compute the amount of padding needed in each dimension
    """pad_y = max(0, y2 - actual_y2)
    pad_x = max(0, x2 - actual_x2)
    
    # Pad the sliced array if necessa#ry
    if pad_y > 0 or pad_x > 0:
        #padded_arr = np.pad(sliced_arr, ((0, pad_y), (0, pad_x),(0,0)), mode='constant')

        print("PADDING",padded_arr.shape)
    else:
        padded_arr = sliced_arr
        print("NO-PADDING", padded_arr.shape)""
    
    return padded_arr,current_size"""

def handle_image_size(input_image, dimension,smooth_window_shape =(0,0)):
    img_parts = []
    shape_parts = []
    
    h, w, _ = input_image.shape

    rows_num =int(ceil(h/dimension[0]))
    cols_num = int(ceil(w/dimension[1]))

    for row in range(rows_num):
        row_parts =[]
        row_shapes = []
        
        row_start =row*dimension[0] 
        row_end = (row+1)*dimension[0]
        """if row != 0:
            row_start -= smooth_window_shape[0]
            row_end -= smooth_window_shape[0]"""

        for col in range(cols_num):
            col_start = col*dimension[1]
            col_end =(col+1)*dimension[1]
            """if col != 0:
                col_start -= smooth_window_shape[1]
                col_end -= smooth_window_shape[1]"""

            tl,br = (row_start,col_start),(row_end,col_end)
            img,shape = slice_and_pad_array(input_image,tl,br,dimension)
            row_parts.append(img)
            row_shapes.append(shape)
        img_parts.append(row_parts)
        shape_parts.append(row_shapes)
    
    return img_parts,shape_parts

def handle_image_size2(input_image: np.ndarray, dimension: tuple):
    
    assert input_image.ndim == 3, (
        "Image should have 3 dimension '[HxWxC]'" "got %s",
        (input_image.shape,),
    )

    assert len(dimension) == 2, (
        "'dimension' should have 'Hxw' " "got %s",
        (dimension,),
    )

    h, w, _ = input_image.shape

    if dimension < (h, w): #image bigger than max dimension
        random_height, random_width = get_random_crop_x_and_y(dimension, (h, w))
        input_image = crop_image(input_image, dimension, (random_height, random_width))

    elif dimension > (h, w): #image bigger than max dimension
        limit = get_pad_limit(dimension, (h, w))
        input_image = pad_image(input_image, limit)

    return input_image

