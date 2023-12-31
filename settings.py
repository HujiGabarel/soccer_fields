import os
import math

VIABLE_LANDING = 255
UNVIABLE_LANDING = 0
SHP_PATH = "../../SHP_UTM/B_BUILDINGS_A.shp"
DTM_FILE_PATH = "../../DTM_data/dtm_Israel.tif"
TRAINED_MODEL_PATH = "../../Models/official_masks_10%.joblib"  # The trained model
E_INITIAL_VALUE, N_INITIAL_VALUE, RADIUS_INIT_VALUE = "698812", "3620547", "0.2"
TIME_FOR_KM_AREA = 300  # in seconds
# GUI
dir_path = os.path.dirname(os.path.realpath(__file__))
search_path = os.path.join(dir_path, 'Modules/Front/images_for_gui/heli_logo.jpeg')
cell_path = os.path.join(dir_path, 'Modules/Front/images_for_gui/cell2.png')
logo_path = os.path.join(dir_path, 'Modules/Front/images_for_gui/logo.png')
# HELICOPTER_IMAGE_PATH = os.path.join(dir_path, 'images_for_gui/yasor.jpg')
ORIGINAL_IMAGE_PATH = logo_path
RESULT_IMAGE_PATH = logo_path
TREES_IMAGE_PATH = os.path.join(dir_path, 'Modules/Front/images_for_gui/Trees.png')
BUILDINGS_IMAGE_PATH = os.path.join(dir_path, 'Modules/Front/images_for_gui/Buildings.png')
SLOPES_IMAGE_PATH = os.path.join(dir_path, 'Modules/Front/images_for_gui/Slopes.png')
ELECTRICITY_IMAGE_PATH = os.path.join(dir_path, 'Modules/Front/images_for_gui/electrical_line.png')

FONT = ('Helvetica', 16, "bold")
FONT_SMALL = ('Helvetica', 8, "bold")
BACKGROUND_COLOR = 'white'
SECOND_BACKGROUND_COLOR = '#7EB8E3'
FOREGROUND_COLOR = 'black'
# distance text color that will stand out on the background, (not white) and not black
E_LABEL_LOCATION = (0.41, 0.05)
E_ENTRY_LOCATION = (0.5, 0.05)
N_LABEL_LOCATION = (0.41, 0.1)
N_ENTRY_LOCATION = (0.5, 0.1)
R_LABEL_LOCATION = (0.39, 0.15)
R_ENTRY_LOCATION = (0.5, 0.15)
DISTANCE_ENTRY_LOCATION = (0.8, 0.3)
FILE_PATH_LABEL_LOCATION = (0.15, 0.45)
FILE_PATH_BROWSE_LOCATION = (0.15, 0.5)
LABEL_FILE_PATH_WIDTH = 20
LINE_WIDTH = 3
LINE_COLOR = "#7B68EE"
DISTANCE_LABEL_COLOR = 'white'
DISTANCE_TEXT_COLOR = LINE_COLOR
DISTANCE_FONT = ('Helvetica', 10, "bold")
DISTANCE_LABEL_WIDTH = 6
DISTANCE_LABEL_HEIGHT = 1
WINDOW_X, WINDOW_Y, WINDOW_SQUARE_X, WINDOW_SQUARE_Y = 500, 500, 50, 20
CANVAS_LOCATION = (0.5, 0.58)
CANVAS_WIDTH, CANVAS_HEIGHT = 500, 500
SLIDER_WIDTH, SLIDER_LENGTH = 15, 20
SLIDER_LOCATION = (0.32, CANVAS_LOCATION[1])
PROGRESSBAR_WIDTH, PROGRESSBAR_LENGTH = 15, 200
PROGRESSBAR_LOCATION = (0.5, 0.96)
PROGRESSBAR_LOCATION_LABEL = (0.5, 0.92)
SEARCH_BUTTON_LOCATION = (0.5, 0.221)
SEARCH_BUTTON_WIDTH, SEARCH_BUTTON_HEIGHT = 30, 30
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
# MASKS_KEYS = ["Slopes", "Buildings", "Trees", "Electricity", "Buildings&Slopes", "Slopes&Trees", "Electricity&Slopes",
#               "Electricity&Trees", "Buildings&Trees", "Buildings&Electricity", "Buildings&Slopes&Trees",
#               "Buildings&Electricity&Slopes", "Electricity&Slopes&Trees", "Buildings&Electricity&Trees",
#               "Buildings&Electricity&Slopes&Trees"]
MASKS_KEYS = ["Slopes", "Trees", "Slopes&Trees", "Buildings", "Electricity",
              "Buildings&Slopes&Trees"]
SLOPES_CHECK_BOX_LOCATION = (0.8, 0.3)
BUILDINGS_CHECK_BOX_LOCATION = (0.8, 0.38)
TREES_CHECK_BOX_LOCATION = (0.8, 0.46)
ELECTRICITY_CHECK_BOX_LOCATION = (0.8, 0.54)

CHECK_BOX_IMAGE_WIDTH, CHECK_BOX_IMAGE_HEIGHT = 50, 50

TWO_POINTS_DISTANCE = lambda x, y, START_X, START_Y, END_X, END_Y: abs(
    (END_Y - START_Y) * x - (END_X - START_X) * y + END_X * START_Y - END_Y * START_X) / \
                                                                   math.sqrt(
                                                                       (END_Y - START_Y) ** 2 + (END_X - START_X) ** 2)
