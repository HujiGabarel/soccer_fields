import sys
import tkinter as tk
from PIL import ImageTk
import numpy as np

from Modules.Front import utils

sys.path.append('../..')

# from Modules.Main.Main import get_viable_landing_in_radius
import cv2
import threading
from PIL import Image
from tkinter import ttk
import time
from settings import *
from tkinter import filedialog


def distance_text_location_func(points):
    x = (points[0] + points[2]) // 2
    y = (points[1] + points[3]) // 2
    padding = 25
    x_1, y_1 = x - padding, y - padding
    x_2, y_2 = x + padding, y + padding
    points_list = [(x_1, y_1), (x_2, y_2), (x_1, y_2), (x_2, y_1)]
    max_point = max(points_list,
                    key=lambda point: TWO_POINTS_DISTANCE(point[0], point[1], START_X, START_Y, END_X, END_Y))
    max_distance = TWO_POINTS_DISTANCE(max_point[0], max_point[1], START_X, START_Y, END_X, END_Y)
    far_points = [point for point in points_list if
                  max_distance < TWO_POINTS_DISTANCE(point[0], point[1], START_X, START_Y, END_X, END_Y) + 2]
    max_point = max(far_points,
                    key=lambda point: min(point[0], point[1], CANVAS_WIDTH - point[0], CANVAS_HEIGHT - point[1]))
    x_gap, y_gap = max_point[0] - x, max_point[1] - y
    return x + x_gap, y + y_gap


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.file_path = []
        self.configure(background=BACKGROUND_COLOR)
        self.title("Soccer Field")
        self.canvas_distance = {}
        self.entry_distance_labels = {}
        self.list_mask = []
        self.check_box_list = []
        self.check_box_images = []

        self.geometry("1400x800")
        self.line = -111

        # self.state("zoomed")

        self.resizable(False, False)
        self.create_widgets()
        self.init_logo_image()
        self.init_with_values()
        self.bind_keys()

    def init_with_values(self, E=E_INITIAL_VALUE, N=N_INITIAL_VALUE, Radius=RADIUS_INIT_VALUE):
        self.E_entry.insert(0, E)
        self.N_entry.insert(0, N)
        self.Radius_entry.insert(0, Radius)

    def init_logo_image(self):
        self.add_original_image(self.original_image_array)
        self.add_result_image(self.result_image_array)

    def create_widgets(self):
        self.add_inputs_cells()
        self.add_search_button()
        self.add_progressbar()
        self.add_images_and_canvas()

        self.add_slider()
        self.add_masks_check_boxes()
        # self.add_load_file_button()
        # self.create_type_label()
        # self.change_type_button()

    # Set the key bindings
    def bind_keys(self):
        self.canvas.bind("<Button-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<Button-3>", self.delete_line)

    # Add input cells
    def add_inputs_cells(self):
        self.load_cell_image()
        self.add_E_cell()
        self.add_N_cell()
        self.add_R_cell()

    def add_cell(self, text, label_location, label, entry_location, entry):
        # TODO: FIX LEBAL AND TEXT
        text_label = tk.Label(self, text=text)
        text_label.place(relx=label_location[0], rely=label_location[1], anchor=tk.CENTER)
        text_label.config(font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        label.pack()
        label.place(relx=entry_location[0], rely=entry_location[1], anchor=tk.CENTER)
        entry.pack()
        entry.place(relx=entry_location[0], rely=entry_location[1], anchor=tk.CENTER)
        entry.config(width=CELL_WIDTH - 250, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR,
                     font=FONT,
                     justify=tk.CENTER, bd=0, highlightthickness=0)

    def load_cell_image(self):
        self.cell_image = Image.open(cell_path)
        self.cell_image = self.cell_image.resize((CELL_WIDTH, CELL_HEIGHT), Image.ANTIALIAS)
        self.cell_image = ImageTk.PhotoImage(self.cell_image)

    def add_E_cell(self):
        self.E_label = tk.Label(self, image=self.cell_image, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        self.E_entry = tk.Entry(self)
        self.add_cell("E:", E_LABEL_LOCATION, self.E_label, E_ENTRY_LOCATION, self.E_entry)

    def add_N_cell(self):
        self.N_label = tk.Label(self, image=self.cell_image, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        self.N_entry = tk.Entry(self)
        self.add_cell("N:", N_LABEL_LOCATION, self.N_label, N_ENTRY_LOCATION, self.N_entry)

    def add_R_cell(self):
        self.Radius_label = tk.Label(self, image=self.cell_image, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        self.Radius_entry = tk.Entry(self)
        self.add_cell("Radius:", R_LABEL_LOCATION, self.Radius_label, R_ENTRY_LOCATION, self.Radius_entry)

    # Add search button
    def add_search_button(self):
        self.search_image = Image.open(search_path)
        self.search_image = self.search_image.resize((SEARCH_BUTTON_WIDTH, SEARCH_BUTTON_HEIGHT))
        self.search_image = ImageTk.PhotoImage(self.search_image)
        self.search_button = tk.Button(self, image=self.search_image, command=self.search, bg=BACKGROUND_COLOR, bd=0,
                                       highlightthickness=0, activebackground=BACKGROUND_COLOR,
                                       text="Search", font=FONT, compound="top", borderwidth=0.5)
        self.search_button.pack()
        self.search_button.place(relx=SEARCH_BUTTON_LOCATION[0], rely=SEARCH_BUTTON_LOCATION[1], anchor=tk.CENTER)

    def create_inputs_cells(self):
        self.add_E_cell()
        self.add_N_cell()
        self.add_R_cell()

    def add_trees_check_box(self):
        self.trees_check_point = tk.IntVar()
        self.trees_check_box = tk.Checkbutton()
        self.add_check_box(TREES_IMAGE_PATH, TREES_CHECK_BOX_LOCATION, " Trees" + " " * 7, self.trees_check_point,
                           self.trees_check_box)

    def add_buildings_check_box(self):
        self.buildings_check_point = tk.IntVar()
        self.buildings_check_box = tk.Checkbutton()
        self.add_check_box(BUILDINGS_IMAGE_PATH, BUILDINGS_CHECK_BOX_LOCATION, " Buildings" + " "* 1, self.buildings_check_point,
                           self.buildings_check_box)

    def add_electricity_check_box(self):
        # For Future use , not implemented yet
        # TODO: IMPLEMENT and add to the list
        electricity_image = Image.open(ELECTRICITY_IMAGE_PATH).resize((CHECK_BOX_IMAGE_WIDTH, CHECK_BOX_IMAGE_HEIGHT))
        self.electricity_image = ImageTk.PhotoImage(electricity_image)
        self.electricity_check_point = tk.IntVar()
        self.electricity_check_point.set(0)
        self.electricity_check_box = tk.Checkbutton(self, variable=self.electricity_check_point,
                                                    command=self.check_box_changed, text=" Electricity",
                                                    image=self.electricity_image,
                                                    compound="left", font=FONT, foreground=FOREGROUND_COLOR,
                                                    background=BACKGROUND_COLOR)
        self.electricity_check_box.place(relx=ELECTRICITY_CHECK_BOX_LOCATION[0], rely=ELECTRICITY_CHECK_BOX_LOCATION[1],
                                         anchor=tk.CENTER)
        # self.check_box_list.append(self.electricity_check_box) # Add to list of check boxes

    def add_slopes_check_box(self):
        self.slope_check_point = tk.IntVar()
        self.slope_check_box = tk.Checkbutton(self)
        self.add_check_box(SLOPES_IMAGE_PATH, SLOPES_CHECK_BOX_LOCATION, " Terrain" + " "*5, self.slope_check_point,
                           self.slope_check_box)

    def add_check_box(self, check_box_path, check_box_location, text, check_point, check_box):
        check_box_image = Image.open(check_box_path).resize((CHECK_BOX_IMAGE_WIDTH, CHECK_BOX_IMAGE_HEIGHT))
        self.check_box_image = ImageTk.PhotoImage(check_box_image)
        self.check_box_images.append(self.check_box_image)
        check_box.config(variable=check_point, command=self.check_box_changed,
                         text=text, image=self.check_box_images[-1], compound="left",
                         font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        check_box.place(relx=check_box_location[0], rely=check_box_location[1], anchor=tk.CENTER)
        check_point.set(1)

        self.check_box_list.append(check_box)

    def add_masks_check_boxes(self):
        self.add_slopes_check_box()
        self.add_buildings_check_box()
        self.add_trees_check_box()
        self.add_electricity_check_box()

    def check_box_changed(self):
        if self.list_mask == []:
            return None
        # if self.slope_check_point.get() == 0:
        #     index_mask = len(self.list_mask) - 3
        #     self.add_image_and_result_image(self.saved_og_image, self.list_mask[index_mask])
        #     self.change_other_check_boxes(index_mask, False)
        # elif self.buildings_check_point.get() == 0:
        #     index_mask = len(self.list_mask) - 2
        #     self.add_image_and_result_image(self.saved_og_image, self.list_mask[index_mask])
        #     self.change_other_check_boxes(index_mask, False)
        # elif self.trees_check_point.get() == 0:
        #     index_mask = len(self.list_mask) - 1
        #     self.add_image_and_result_image(self.saved_og_image, self.list_mask[index_mask])
        #     self.change_other_check_boxes(index_mask, False)
        if self.trees_check_point.get() == 1:
            index_mask = len(self.list_mask) - 1
            self.add_image_and_result_image(self.saved_og_image, self.list_mask[index_mask])
            self.change_other_check_boxes(index_mask)
        elif self.buildings_check_point.get() == 1:
            index_mask = len(self.list_mask) - 2
            self.add_image_and_result_image(self.saved_og_image, self.list_mask[index_mask])
            self.change_other_check_boxes(index_mask)
        elif self.slope_check_point.get() == 1:
            index_mask = len(self.list_mask) - 3
            self.add_image_and_result_image(self.saved_og_image, self.list_mask[index_mask])
            self.change_other_check_boxes(index_mask)

        self.update_transparency(50)  # TODO: change to the current transparency
        self.save_distance_when_mask_changed()

    def change_other_check_boxes(self, last_index_mask, select_all=True):
        """
        when check box is changed, this function is called to change the other check boxes correspondingly
        :param last_index_mask:
        :param select_all: select all the checkboxes if true, if false, deselect all the checkboxes
        :return:
        """
        if select_all:
            for i in range(len(self.check_box_list[0:last_index_mask + 1])):
                self.check_box_list[i].select()
        else:
            for check_box in self.check_box_list[last_index_mask:]:
                check_box.deselect()

    # Distance functions and visualization
    def draw_line(self, START_X, START_Y, END_X, END_Y):
        if self.line != -111:
            self.canvas.coords(self.line, START_X, START_Y, END_X, END_Y)
            self.canvas_distance[self.line] = [START_X, START_Y, END_X, END_Y]
        else:
            self.line = self.canvas.create_line(START_X, START_Y, END_X, END_Y, width=LINE_WIDTH, fill=LINE_COLOR,
                                                smooth=True)
            self.canvas_distance[self.line] = [START_X, START_Y, END_X, END_Y]
        # calculate the distance between the two points
        self.distance = math.sqrt((START_X - END_X) ** 2 + (START_Y - END_Y) ** 2)
        float_R = 1 if float(self.Radius_entry.get()) == 0 else float(self.Radius_entry.get())
        self.distance = 2 * self.distance * float_R * 1000 / CANVAS_WIDTH
        self.distance = round(self.distance, 2)
        self.add_entry_distance()

    def search(self):
        self.update_progressbar(0)
        self.E_value = self.E_entry.get()
        self.N_value = self.N_entry.get()
        self.Radius_value = self.Radius_entry.get()
        coordinates = (int(self.E_value), int(self.N_value), 36, "N")
        print(coordinates, self.Radius_value)  # TODO: add log
        t = threading.Thread(target=self.run_process, args=(coordinates,))
        t.start()
        progress_thread = threading.Thread(target=self.run_progressbar())
        progress_thread.start()

    def run_process(self, coordinates):
        image, self.list_mask = utils.send_request(coordinates, float(self.Radius_value))
        # image, self.list_mask = get_viable_landing_in_radius(coordinates, float(self.Radius_value), self)
        self.add_original_image(image)
        self.add_result_image(self.list_mask[-1])  # TODO: need to be general
        self.update_transparency(50)

    def start(self, event):
        global START_X, START_Y
        self.line = -111
        START_X, START_Y = event.x, event.y
        # Define a function to update the end point of the line and draw it

    def draw(self, event):
        global START_X, START_Y, END_X, END_Y
        if START_X and START_Y:
            END_X, END_Y = event.x, event.y
            if self.line != -111:
                self.canvas.coords(self.line, START_X, START_Y, END_X, END_Y)
                self.canvas_distance[self.line] = [START_X, START_Y, END_X, END_Y]
            else:
                self.line = self.canvas.create_line(START_X, START_Y, END_X, END_Y, width=LINE_WIDTH, fill=LINE_COLOR,
                                                    smooth=True)
                self.canvas_distance[self.line] = [START_X, START_Y, END_X, END_Y]
            # calculate the distance between the two points
            self.distance = math.sqrt((START_X - END_X) ** 2 + (START_Y - END_Y) ** 2)
            float_R = 1 if float(self.Radius_entry.get()) == 0 else float(self.Radius_entry.get())
            self.distance = 2 * self.distance * float_R * 1000 / CANVAS_WIDTH
            self.distance = round(self.distance, 2)
            self.add_entry_distance()

    def delete_line(self, event):
        x, y = event.x, event.y
        distances_from_point = {}
        for line in self.canvas_distance:
            # check what line is clicked, and delete it
            # the line that is clicked is the line that is closest to the point that is clicked
            # the distance between the point and the line is the shortest distance between the point and a point on the line
            START_X, START_Y, END_X, END_Y = self.canvas_distance[line]
            # calculate the distance between the point and the line
            distance = TWO_POINTS_DISTANCE(x, y, START_X, START_Y, END_X, END_Y)
            distances_from_point[line] = distance
        # find the line that is closest to the point that is clicked
        if len(self.canvas_distance) == 0:
            return
        closest_line = min(distances_from_point, key=distances_from_point.get)
        # delete the line
        self.canvas.delete(closest_line)
        # delete the line from the dictionary
        # self.entry_distance_labels[closest_line].place_forget()
        self.canvas.delete(self.entry_distance_labels[closest_line])
        # place the entry distance label on the canvas above the line that in position (x1,y1) and (x2,y2)
        del self.canvas_distance[closest_line]
        del self.entry_distance_labels[closest_line]

    def add_entry_distance(self):
        if self.line == -111:
            return None
        if self.line in self.entry_distance_labels:
            X, Y = distance_text_location_func(self.canvas_distance[self.line])
            self.canvas.delete(self.entry_distance_labels[self.line])
            self.entry_distance_labels[self.line] = self.canvas.create_text((X, Y),
                                                                            text=DISTANCE_STR_FORMAT(self.distance),
                                                                            font=DISTANCE_FONT,
                                                                            fill=DISTANCE_TEXT_COLOR)
            return None
        self.entry_distance_labels[self.line] = self.canvas.create_text(DISTANCE_ENTRY_LOCATION,
                                                                        text=DISTANCE_STR_FORMAT(self.distance),
                                                                        font=DISTANCE_FONT, fill=DISTANCE_TEXT_COLOR)
    def save_distance_when_mask_changed(self):
        for distance in self.entry_distance_labels:
            self.canvas.delete(self.entry_distance_labels[distance])
        self.entry_distance_labels = {}
        for line in self.canvas_distance.keys():
            self.canvas.delete(line)
        canvas_distance_copy = self.canvas_distance.copy()
        self.canvas_distance = {}
        self.entry_distance_labels = {}
        for line in canvas_distance_copy:
            self.line = -111
            P = canvas_distance_copy[line]
            self.draw_line(P[0], P[1], P[2], P[3])

    # Canvas, Image functions and visualization (transparency)
    def add_images_and_canvas(self):
        self.original_image = Image.open(ORIGINAL_IMAGE_PATH)
        self.result_image = Image.open(RESULT_IMAGE_PATH)
        self.original_image_array = np.array(self.original_image)
        self.result_image_array = np.array(self.result_image)
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white",
                                highlightcolor=CANVAS_HIGHLIGHT_COLOR)
        self.canvas.place(relx=CANVAS_LOCATION[0], rely=CANVAS_LOCATION[1], anchor=tk.CENTER)

    def update_transparency(self, val):
        alpha = TRANSPARENCY_FUNCTION(val)
        cop = self.result_image_1.copy()
        cop.putalpha(alpha)
        alpha_image = ImageTk.PhotoImage(cop)
        self.canvas.itemconfig(self.result_image_canvas, image=alpha_image)
        self.canvas.image = alpha_image
        self.transparency_slider.set(val)

    def add_slider(self):
        self.transparency_slider = tk.Scale(self, from_=0, to=100, orient=tk.VERTICAL, length=CANVAS_HEIGHT,
                                            width=SLIDER_WIDTH,
                                            sliderlength=SLIDER_LENGTH,
                                            background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR,
                                            command=self.update_transparency)
        self.transparency_slider.pack()
        self.transparency_slider.place(relx=SLIDER_LOCATION[0], rely=SLIDER_LOCATION[1], anchor=tk.CENTER)
        self.transparency_slider.set(100)

    # Add images to the canvas
    def add_original_image(self, image):
        """
        get the original image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 200
        :param image: the original image
        :return:
        """
        self.saved_og_image = image
        self.original_image_1 = Image.fromarray(cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2RGB)).resize((WINDOW_X, WINDOW_Y))
        self.original_image = ImageTk.PhotoImage(self.original_image_1)
        self.canvas.create_image(0, 0, image=self.original_image, anchor=tk.NW)

    def add_result_image(self, image):
        """
        get the result image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 420
        :param image: the result image
        :return:
        """
        # if self.list_mask == []:
        #     self.list_mask = {k: image for k in MASKS_KEYS}
        self.result_image_1 = Image.fromarray(image).resize((WINDOW_X, WINDOW_Y))
        self.result_image_1 = self.result_image_1.convert(mode='RGB')
        self.result_image = ImageTk.PhotoImage(self.result_image_1)
        self.result_image_canvas = self.canvas.create_image(0, 0, image=self.result_image, anchor=tk.NW)
        # self.add_square_image()

    def add_image_and_result_image(self, saved_og_image, mask):
        self.add_original_image(saved_og_image)
        self.add_result_image(mask)
        return

    # PROGRESSBAR
    def create_style_progressbar(self):
        pb_style = ttk.Style()
        pb_style.theme_use("default")
        pb_style.layout('text.Horizontal.TProgressbar',
                        [('Horizontal.Progressbar.trough',
                          {'children': [('Horizontal.Progressbar.pbar',
                                         {'side': 'left', 'sticky': 'ns'})],
                           'sticky': 'nswe'}),
                         ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
        pb_style.configure('text.Horizontal.TProgressbar', anchor='center',
                           background=SECOND_BACKGROUND_COLOR, )

    def add_progressbar(self):
        self.create_style_progressbar()
        self.progressbar = ttk.Progressbar(self, orient="horizontal", length=PROGRESSBAR_LENGTH, mode="determinate",
                                           style="text.Horizontal.TProgressbar")
        self.progressbar.place(relx=PROGRESSBAR_LOCATION[0], rely=PROGRESSBAR_LOCATION[1], anchor=tk.CENTER)
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        self.progressbar_label = tk.Label(self, text="0%", font=FONT, foreground=FOREGROUND_COLOR,
                                          background=BACKGROUND_COLOR)
        self.progressbar_label.place(relx=PROGRESSBAR_LOCATION_LABEL[0], rely=PROGRESSBAR_LOCATION_LABEL[1],
                                     anchor=tk.CENTER)

    def update_progressbar(self, value):
        self.progressbar_label.config(text=f"{value}%")
        self.progressbar["value"] = value
        self.progressbar.update()

    def run_progressbar(self):
        self.time_for_iteration = (TIME_FOR_KM_AREA * (2 * (float(self.Radius_entry.get())) ** 2) / 100)
        while self.progressbar['value'] < 99:
            current_value = self.progressbar['value']
            self.update_progressbar(current_value + 1)
            print(self.time_for_iteration, self.progressbar['value'])
            time.sleep(self.time_for_iteration)  # 70 sec per km^2, total time = 0.1 * (2R)^2, itreatiiom time=
        else:
            print('Progresbar complete!')

    def update_progressbar_speed(self, val):
        self.time_for_iteration = val

    # NOT IN USE - FOR FUTURE USE
    def change_type_button(self):
        self.size_button = tk.Button(self, text="Change Type", command=self.update_size)
        self.size_button.pack()
        self.size_button.place(relx=0.2, rely=0.7, anchor=tk.CENTER)
        self.size_button.config(background=SECOND_BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, font=FONT)

    def create_type_label(self):
        self.type_label = tk.Label(self, text="יסעור", font=FONT, foreground=FOREGROUND_COLOR,
                                   background=SECOND_BACKGROUND_COLOR)
        self.type_label.place(relx=0.2, rely=0.6, anchor=tk.CENTER)

    def update_size(self):
        # change the size of the square image to fit the helicopter type
        if self.type_label["text"] == "יסעור":
            self.type_label["text"] = "ינשוף"
            self.square_x = 50
            self.square_y = 20
        elif self.type_label["text"] == "ינשוף":
            self.type_label["text"] = "יסעור"
            self.square_x = 70
            self.square_y = 200
        self.add_square_image()

    def get_Radius_value(self):
        return self.Radius_value

    def add_load_file_button(self):
        # Create a label and entry widget to display the selected file name
        self.file_name = tk.StringVar()
        file_path_label = tk.Label(self, textvariable=self.file_name, width=LABEL_FILE_PATH_WIDTH, font=FONT,
                                   foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        file_path_label.place(relx=FILE_PATH_LABEL_LOCATION[0], rely=FILE_PATH_LABEL_LOCATION[1], anchor=tk.CENTER)
        # Create a button to browse and select the file
        browse_button = tk.Button(self, text="Browse File", command=self.browse_file, background=BACKGROUND_COLOR,
                                  foreground=FOREGROUND_COLOR, font=FONT, borderwidth=0.5)
        browse_button.place(relx=FILE_PATH_BROWSE_LOCATION[0], rely=FILE_PATH_BROWSE_LOCATION[1], anchor=tk.CENTER)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path.append(file_path)
        print("Selected file path:", file_path)
        self.file_name.set(os.path.basename(file_path))  # Extract the file name from the path

    def get_shp_file_path(self):
        return self.file_path

    def add_label_list_of_files_loaded(self):
        pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    if len(sys.argv) == 1:
        SERVER_HOST = '127.0.0.1'
        SERVER_LISTEN_PORT = 2222
    elif len(sys.argv) == 2:
        SERVER_HOST = sys.argv[1]
        SERVER_LISTEN_PORT = 2222
    elif len(sys.argv) == 3:
        SERVER_HOST = sys.argv[1]
        SERVER_LISTEN_PORT = sys.argv[2]
    else:
        print("Usage: python main.py [SERVER_HOST] [SERVER_LISTEN_PORT]")
        exit(1)
    utils.url = f'http://{SERVER_HOST}:{SERVER_LISTEN_PORT}/calc'
    gui = GUI()
    gui.mainloop()
    print("Done!")
