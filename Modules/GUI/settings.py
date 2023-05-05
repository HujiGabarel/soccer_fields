import os
import math
# Get the directory path of the current file (gui.py)
dir_path = os.path.dirname(os.path.realpath(__file__))
search_path = os.path.join(dir_path, 'images_for_gui/heli_logo.jpeg')
cell_path = os.path.join(dir_path, 'images_for_gui/cell2.png')
# Construct the absolute path of logo.png
logo_path_gif = os.path.join(dir_path, 'images_for_gui/LOGO.gif')
logo_path = os.path.join(dir_path, 'images_for_gui/logo.png')
# Construct the absolute path of background.png
pnotnp_path = os.path.join(dir_path, 'images_for_gui/PNOTNP.jpg')
# Construct the absolute path of background.png
pnp_path = os.path.join(dir_path, 'images_for_gui/PNP.jpg')
# Construct the absolute path of background.png
HELICOPTER_IMAGE_PATH = os.path.join(dir_path, 'images_for_gui/yasor.jpg')
# Construct the absolute path of the original image and result image
ORIGINAL_IMAGE_PATH = logo_path
RESULT_IMAGE_PATH = logo_path
FONT = ('Helvetica', 16, "bold")
FONT_SMALL = ('Helvetica', 8, "bold")
BACKGROUND_COLOR = 'white'
SECOND_BACKGROUND_COLOR = '#7EB8E3'
FOREGROUND_COLOR = 'black'
# distance text color that will stand out on the background, (not white) and not black
DISTANCE_TEXT_COLOR = SECOND_BACKGROUND_COLOR
ENTRY_WIDTH = 20
E_LABEL_LOCATION = (0.41, 0.05)
E_ENTRY_LOCATION = (0.5, 0.05)
N_LABEL_LOCATION = (0.41, 0.1)
N_ENTRY_LOCATION = (0.5, 0.1)
R_LABEL_LOCATION = (0.375, 0.15)
R_ENTRY_LOCATION = (0.5, 0.15)
DISTANCE_ENTRY_LOCATION = (0.8, 0.3)

LINE_WIDTH = 3
LINE_COLOR = SECOND_BACKGROUND_COLOR
DISTANCE_LABEL_COLOR = 'white'
DISTANCE_LABEL_WIDTH = 6
DISTANCE_LABEL_HEIGHT = 1
WINDOW_X, WINDOW_Y, WINDOW_SQUARE_X, WINDOW_SQUARE_Y = 500, 500, 50, 20
CANVAS_LOCATION = (0.5, 0.58)
CANVAS_WIDTH, CANVAS_HEIGHT = 500, 500
SLIDER_WIDTH, SLIDER_LENGTH = 15, 20
SLIDER_LOCATION = (0.32, CANVAS_LOCATION[1])
POGRESSBAR_WIDTH, PROGRESSBAR_LENGTH = 15, 200
POGRESSBAR_LOCATION = (0.5, 0.96)
POGRESSBAR_LOCATION_LABEL = (0.5, 0.92)
SEARCH_BUTTON_LOCATION = (0.5, 0.22)
SEARCH_BUTTON_WIDTH, SEARCH_BUTTON_HEIGHT = 70, 70
CELL_WIDTH, CELL_HEIGHT = 250, 50
CANVAS_HIGHLIGHT_COLOR = "red"
TRANSPARENCY_FUNCTION = lambda val: int(float(val) * 255 / 100)
ROTATION_KEY = "1"
DISTANCE_STR_FORMAT = lambda x: f"{x} m"
VIEWPORT_X = 0
VIEWPORT_Y = 0
VIEWPORT_WIDTH = CANVAS_WIDTH
VIEWPORT_HEIGHT = CANVAS_HEIGHT
START_X, START_Y = None, None
END_X, END_Y = None, None


TWO_POINTS_DISTANCE = lambda x, y, START_X, START_Y, END_X, END_Y: abs(
    (END_Y - START_Y) * x - (END_X - START_X) * y + END_X * START_Y - END_Y * START_X) / \
                                                                   math.sqrt(
                                                                       (END_Y - START_Y) ** 2 + (END_X - START_X) ** 2)
