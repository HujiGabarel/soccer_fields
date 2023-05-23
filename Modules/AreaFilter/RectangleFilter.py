import numpy as np
import time
from shapely import box,Point, union_all
import matplotlib.pyplot as plt


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

def detect_rectangles(matrix,shape,val_to_find,threshold = 0):   
    """
    finding rectangles in the requested shape which contain only val_to_find

    :param sum_matrix: input matrix
    :param shape: shape of rectangle to check - will loop also for Transpose(shape) 
    :param shape: value to find for in rectangle
    :param threshold: value between 0 and 1 for detecting "almost full" rectangles
    :return:     result as: list [(tl,br)...] -> [((row_tl,col_tl),(row_br,col_br))...]
    """

    #change values in order to 
    VALUE_REPLACEMENT = 1
    if val_to_find == VALUE_REPLACEMENT:
        VALUE_REPLACEMENT += 1
    
    matrix = np.copy(matrix)
    matrix[matrix != val_to_find] = VALUE_REPLACEMENT
    matrix[matrix == val_to_find] = 0


    wanted_sum = shape[0]*shape[1] *threshold
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



def smooth_unwanted(matrix,shape,val_to_find = 255, threshold=0):
    """_summary_

    :param matrix: _description_
    :type matrix: _type_
    :param shape: _description_
    :type shape: _type_
    :param val_to_find: _description_, defaults to 0
    :type val_to_find: int, optional
    :param threshold: _description_, defaults to 0
    :type threshold: int, optional
    """
    #list to dict
    final_res = np.zeros(dtype=np.int32,shape=matrix.shape)

    t1 = time.time()
    all_rectangles_indices = detect_rectangles(matrix,shape,val_to_find,threshold)
    events = {}

    print("rectangles found: ",len(all_rectangles_indices))
    for rectangle in all_rectangles_indices:
        (row_tl, col_tl), (row_br, col_br) = rectangle
        for i in range(row_tl,row_br+1):
            if i not in events.keys():
                events[i] = []
            events[i].append((col_tl, 'start'))
            events[i].append((col_br, 'end'))

    t2 = time.time() 
    print("create data ",(t2-t1)*1000)
       
    t1 = time.time()
    for y,events_y in events.items():
        counter = 0
        start_x = -1
        for x, event_type, in events_y:
            
            if x == shape[1]-1 and counter >=1:
                final_res[y,start_x:shape[1]] = 255 #WHITE
                break

            if event_type == 'start':
                counter += 1
                if counter == 1:
                    start_x = x
            
            else:
                counter -=1
                if counter == 0:
                    final_res[y,start_x:x+1] = 255 #WHITE
 
    t2 = time.time()
    """
    for plotting
    print("fill result: ",(t2-t1)*1000)


    fig, axs = plt.subplots(1, 2)

    # Plot matrix1 in the first subplot
    axs[0].imshow(matrix, cmap='viridis')
    axs[0].set_title('before')

    # Plot matrix2 in the second subplot
    axs[1].imshow(final_res, cmap='viridis')
    axs[1].set_title('after')

    # Adjust spacing between subplots
    plt.subplots_adjust(wspace=0.4)

    # Display the plot
    plt.show()"""


    return final_res





