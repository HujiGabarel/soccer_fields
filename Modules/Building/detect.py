import os.path
import sys
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
import time
from imageio import imsave
from torch.utils import model_zoo

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
#from building_footprint_segmentation.utils.operations import handle_image_size,handle_image_size2

from operations import handle_image_size

MAX_SIZE = 384
TRAINED_MODEL = ReFineNet()
MODEL_URL =r"refine.zip"

PRED_PTH = "images/what2.png"
def set_model_weights():
    state_dict = model_zoo.load_url(MODEL_URL, progress=True, map_location="cpu")
    if "model" in state_dict:
        state_dict = state_dict["model"]
    TRAINED_MODEL.load_state_dict(adjust_model(state_dict))


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
    #TODO: predict
    with torch.no_grad():
        # Perform prediction
        t1 = time.time()
        prediction = TRAINED_MODEL(tensor_image)
        t2 =time.time()

        prediction = prediction.sigmoid()
    print((t2-t1)*(10**3))

    #to numpy array
    prediction_binary = convert_tensor_to_numpy(prediction[0]).reshape(
        (MAX_SIZE, MAX_SIZE)
    )

    #TODO: set threshold to set where building
    
    """
    prediction_3_channels = cv2.cvtColor(prediction_binary, cv2.COLOR_GRAY2RGB)

    dst = cv2.addWeighted(
        original_image,
        1,
        (prediction_3_channels * (0, 255, 0)).astype(np.uint8),
        0.4,
        0,
    )
    return prediction_binary, prediction_3_channels, dst"""
    return prediction_binary    
    

def run(image_path):
    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    set_model_weights()
    #img = handle_image_size2(original_image,(MAX_SIZE,MAX_SIZE))
    #extract(img)
    #print(img.shape)
    #input()
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
    print((time.time()-t)*(10**3),"ms")

    return merge_img(results,shapes,original_image.shape[:2])


    # PARALLELIZE the model if gpu available
    # model = load_parallel_model(model)

    """prediction_binary, prediction_3_channels, dst = extract(original_image)
    # imsave(f"{os.path.basename(image_path)}", prediction_binary)
    return prediction_binary, prediction_3_channels, dst"""

original_image = cv2.imread(PRED_PTH)
original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

pred = run(PRED_PTH)
fig,ax = plt.subplots(1,2)
ax = ax.ravel()
print(pred)
ax[0].imshow(original_image)  
ax[1].imshow(pred)
plt.show()
