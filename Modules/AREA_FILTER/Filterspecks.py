import numpy as np
import cv2



# Create a binary matrix
def FilterSpecks(matPicture , size):
        # Save the black and white image to a file
        # matPicture = (matPicture * 255).astype(np.uint8)
        cv2.imwrite("bw_image.png", matPicture)

        # Wait for a key event to close the image window
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        src = cv2.imread('bw_image.png', cv2.IMREAD_GRAYSCALE)

        # convert to binary by thresholding
        ret, binary_map = cv2.threshold(src, 127, 255, 0)

        # do connected components processing
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_map, None, None, None, 8,
                                                                             cv2.CV_32S)

        # get CC_STAT_AREA component as stats[label, COLUMN]
        areas = stats[1:, cv2.CC_STAT_AREA]

        result = np.zeros((labels.shape), np.uint8)

        for i in range(0, nlabels - 1):
                if areas[i] >= size:  # keep
                        result[labels == i + 1] = 255

        # cv2.imshow("Binary", binary_map)
        cv2.imwrite("Binary.png", binary_map)
        cv2.waitKey(0)
        # cv2.imshow("Result", result)

        cv2.destroyAllWindows()

        cv2.imwrite("Filterd_result.png", result)

        # Read the black and white image
        img = cv2.imread('bw_image.png', 0)

        # Threshold the image to obtain foreground and background pixels
        threshold_value = 128
        ret, thresholded_img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)

        # Convert the thresholded image to a binary matrix
        binary_matrix = (thresholded_img > 0).astype(np.uint8)


        return result

if __name__ == '__main__':
    matPicture = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 1, 0, 1, 1, 1, 0],
                            [0, 0, 0, 1, 1, 0, 1, 1, 1, 0],
                            [0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]])
    # produce a binary matrix by 255
    # matPicture = (matPicture / 255).astype(np.uint8)
    print(matPicture)
    size = 8
    FilterSpecks(matPicture, size)