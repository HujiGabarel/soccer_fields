import numpy as np
import time
from shapely import box,Point, union_all

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

from sortedcontainers import SortedDict

def union_rectangles(rectangles):
    events = []
    for rectangle in rectangles:
        (x1, y1), (x2, y2) = rectangle
        events.append((x1, 'start', rectangle))
        events.append((x2, 'end', rectangle))

    events.sort()  # Sort the events by x-coordinate

    active_rectangles = SortedDict()
    union = []
    prev_x = events[0][0]

    for x, event_type, rectangle in events:
        width = x - prev_x

        if active_rectangles:
            max_y = max(rect[3] for rect in active_rectangles.values())
            union.append((prev_x, 0, x, max_y))

        if event_type == 'start':
            active_rectangles[rectangle] = rectangle
        else:
            del active_rectangles[rectangle]

        prev_x = x

    # Generate a set of all unique coordinates inside the union




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
    matrix_dict = np.zeros(dtype=('i4,i4'),shape=matrix.shape) #each  cell in matrix contains tuple(draw_to_right, draw_to left)
    final_res = np.zeros(dtype=np.int32,shape=matrix.shape)

    def list_of_indexes_to_dict(indexes_list):
        for (tl,br) in indexes_list:

            curr = matrix_dict[tl[0],tl[1]]
            height = br[0] - tl[0] +1
            width = br[1] -tl[0] +1
            matrix_dict[tl[0],tl[1]] =(max(height,curr[0]),max(width,curr[1]))

    def list_of_indexes_to_shapes(indexes_list):
        print("num of rectangles found:",len(indexes_list))
        all_shapes = []
        for (tl,br) in indexes_list:
            all_shapes.append(box(*tl,*br))
        

        geometry = union_all(all_shapes)  
        return geometry

    
    all_rectangles_indices = detect_rectangles(matrix,shape,val_to_find,threshold)
    t1 =time.time()
    geometry = list_of_indexes_to_shapes(all_rectangles_indices)
    t2 = time.time()
    print("getting union: ",(t2-t1)*1000)

    t1 =time.time()

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if geometry.contains(Point(i,j)):
                final_res[i,j] = 255 #otherwize zero
    t2 = time.time()
    print("filling matrix: ",(t2-t1)*1000)

    return final_res

    """
    for i in range(shape[0]):
        for j in range(shape[1]):
            curr = matrix_dict[i,j]
            if curr[0] +curr[1] >0: #if in dict
                final_res[i,j] = 255  #TODO: handle values consts(now, black is 0, white is 255)

                #update neighbors
                if i +1 != shape[0] and curr[0] != 1: #need to update 
                    down_neighbor_curr = matrix_dict[i+1,j]
                    
                    matrix_dict[i+1,j] = max(curr[0]-1,down_neighbor_curr[0]),max(curr[1],down_neighbor_curr[1])

                                #update neighbors
                if j +1 != shape[1] and curr[1] != 1: #need to update 
                    right_neighbor_curr = matrix_dict[i,j+1]
                    
                    matrix_dict[i,j+1] = max(curr[0],right_neighbor_curr[0]),max(curr[1]-1,right_neighbor_curr[1])
    
    return matrix_dict
    

    """



    matrix =np.zeros


