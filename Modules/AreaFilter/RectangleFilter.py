import numpy as np
import time

def get_rectangle_sum(sum_matrix,start_point,height,width):
    """inner function - for calculating sum of cells value in rectangle

    :param sum_matrix: summed Area table
    :param start_point: (row,col) - tl of rectangle
    :param height: length of height side
    :param width: length of width side
    :raises Exception: if rectangle out of bounds
    :return: sum of rectangle cells' value
    """
    row_base,col_base = start_point
    next_row = row_base + height-1
    next_col = col_base + width-1

    if row_base < 0 or col_base <0:
        raise Exception("Out of image bounds")    
    if next_row >= sum_matrix.shape[0] or next_col >= sum_matrix.shape[1]:
        raise Exception("Out of image bounds")    
    
    tl_value,bl_value,tr_value = 0,0,0
    if row_base !=0 :
        tr_value = sum_matrix[row_base-1][next_col]
    if col_base != 0:
        bl_value = sum_matrix[next_row][col_base-1] 
    if row_base != 0 and col_base !=0:
        tl_value = sum_matrix[row_base-1][col_base-1]

    val = sum_matrix[next_row][next_col] + tl_value - bl_value - tr_value

    return val

def detect_rectangles(matrix,shape,val_to_find):   
    """
    finding rectangles in the requested shape which contain only val_to_find

    :param sum_matrix: input matrix
    :param shape: shape of rectangle to check - will loop also for Transpose(shape) 
    :param shape: value to find for in rectangle
    :return:     result as: list [(tl,br)...] -> [((row_tl,col_tl),(row_br,col_br))...]
    """

    #change values in order to 
    VALUE_REPLACEMENT = 1
    if val_to_find == VALUE_REPLACEMENT:
        VALUE_REPLACEMENT += 1
    
    matrix = np.copy(matrix)
    matrix[matrix != val_to_find] = VALUE_REPLACEMENT
    matrix[matrix == val_to_find] = 0

    wanted_sum = 0
    t1 = time.time()
    summed = matrix.cumsum(axis=0).cumsum(axis=1)

    results = []
    short_side = min(shape[0],shape[1])

    for i in range(matrix.shape[0]-short_side+1):
        for j in range(matrix.shape[1]-short_side+1):
            try:
                if get_rectangle_sum(summed,(i,j),shape[0],shape[1]) == wanted_sum:
                    results.append(((i,j),(i+shape[0]-1,j+shape[1]-1)))
            except Exception as e:
                pass

            if shape[0] != shape[1]:
                try:
                    if get_rectangle_sum(summed,(i,j),shape[1],shape[0]) == wanted_sum:
                        results.append(((i,j),(i+shape[1]-1,j+shape[0]-1)))
                except Exception as e:
                    pass
    t2 = time.time()
    print((t2-t1)*(10**3),"ms")
    return results

"""
#TODO: should it be in Area_filter?
def detect_fields_in_image(mask,height,width,val_to_find):
    if height > mask.shape[0] or width > mask.shape[1]:
        return []
    
    spots = []
    wanted_spot = np.full((height,width),fill_value=val_to_find) 
    rows, cols = np.where(np.all(np.lib.stride_tricks.sliding_window_view(mask, (height, width)) == wanted_spot, axis=(2, 3))) #axis(2,3) takes size of window
    for  row,col in zip(rows,cols):
        box = ((row,col),(row+height-1,col+width-1))
        spots.append(box)

    return spots

def find_fields(mask,side1,side2,val_to_find):
    #return list of boxes - [((row_tl,col_tl),(row_br,col_br)),...]
    
    spots = detect_fields_in_image(mask,side1,side2,val_to_find)
    if side1 != side2: #check transposed rectangle
        spots = detect_fields_in_image(mask,side2,side1,val_to_find)
    
    return spots
"""
