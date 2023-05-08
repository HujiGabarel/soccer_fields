import os.path
import sys
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
import time
from imageio import imsave
from torch.utils import model_zoo

#TODO: add to globals of project
WHITE_COLOR = 255
BLACK_COLOR = 0

module_path = os.path.abspath(os.path.join('../'))
if module_path not in sys.path:
    sys.path.append(module_path)

from building_footprint_segmentation.seg.binary.models import ReFineNet ,DLinkNet34
from building_footprint_segmentation.helpers.normalizer import min_max_image_net
from building_footprint_segmentation.utils.py_network import (
    to_input_image_tensor,
    add_extra_dimension,
    convert_tensor_to_numpy,
    load_parallel_model,
    adjust_model,
)

from Modules.Building.operations import handle_image_size

MAX_SIZE = 384
TRAINED_MODEL = ReFineNet()
MODEL_URL =r"refine.zip"

PRED_PTH = "images/what2.png"
def set_model_weights():
    state_dict = model_zoo.load_url(MODEL_URL, progress=True, map_location="cpu")
    if "model" in state_dict:
        state_dict = state_dict["model"]
    TRAINED_MODEL.load_state_dict(adjust_model(state_dict))

#mark from res(between 0 and 1) to black and white
def convert_building_to_black_white(mask,threshold = 0.55):
    result = np.zeros(mask.shape,dtype=int)
    result[mask < threshold] = WHITE_COLOR
    result[mask >= threshold] = BLACK_COLOR

    return result

def convert_building_to_tree_style(mask,threshold = 0.35):
    result = np.zeros(mask.shape,dtype=int)
    result[mask < threshold] = 0
    result[mask >= threshold] = 1

    return result

def merge_img(matrix_2d, shapes_to_slice,real_shape,smooth_window_shape=(0,0)):
    
    # Compute the shape of the merged big matrix
    
    # Initialize the merged big matrix with zeros
    merged_matrix = np.zeros(real_shape)
    
    # Loop over each matrix in the 2D matrix of 2D matrices
    row_start = 0
    for row in range(len(matrix_2d)):
        col_start = 0

        for col in range(len(matrix_2d[row])):
            
            # Slice the current matrix according to the shape in the corresponding location in shapes_to_slice
            shape_to_slice,x_indexes,y_indexes = shapes_to_slice[row][col]
            print("pre in merge",y_indexes[0], y_indexes[1],x_indexes[0],x_indexes[1])
            sliced_matrix = matrix_2d[row][col][y_indexes[0] : y_indexes[1] , x_indexes[0]:x_indexes[1]]
            data = sliced_matrix
            print("data in merge",data.shape)
            row_end = row_start + shape_to_slice[0]
            """if row != 0:
                row_end -= smooth_window_shape[0]
                data = data[smooth_window_shape[0]:,:]"""

            col_end = col_start + shape_to_slice[1]
            """if col != 0:
                col_end -= smooth_window_shape[1]
                data = data[:,smooth_window_shape[1]:]"""
            
            #TODO: handle parts of smooth, for example: mean
            # Update the corresponding location in the merged big matrix with the current slice

            merged_matrix[row_start:row_end, col_start:col_end] = data

            # Update the column start index for the next slice
            col_start = col_end
        
        # Update the row start index for the next slice
        row_start = row_end
    
    return merged_matrix    

def extract(original_image):

    # Apply Normalization
    normalized_image = min_max_image_net(img=original_image)

    tensor_image = add_extra_dimension(to_input_image_tensor(normalized_image))
    with torch.no_grad():
        # Perform prediction
        prediction = TRAINED_MODEL(tensor_image)

        prediction = prediction.sigmoid()

    #to numpy array
    prediction_binary = convert_tensor_to_numpy(prediction[0]).reshape(
        (MAX_SIZE, MAX_SIZE)
    )

    #TODO: set threshold to set where building
    return prediction_binary    
    

def detect_building(image_path,threshold=0.45):
    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    set_model_weights()
    imgs,shapes = handle_image_size(original_image,(MAX_SIZE,MAX_SIZE))
    results = []
    t=time.time()
    for i in range(0,len(imgs)):
        row_result =[]
        for j in range(0,len(imgs[i])):
            t1 = time.time()
            row_result.append(extract(imgs[i][j]))
            t2 = time.time()
            print((t2-t1)* 10**3,"ms")
            print("finished",i*len(imgs[i])+j)
        results.append(row_result)
    #print((time.time()-t)*(10**3),"ms")

    pred = merge_img(results,shapes,original_image.shape[:2])
    
    #set threshold
    return pred