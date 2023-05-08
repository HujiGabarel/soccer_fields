import tkinter as tk
from PIL import ImageTk, ImageSequence
import numpy as np
import math

from Modules.Main.Main import get_viable_landing_in_radius
import cv2
import threading
import os
from PIL import Image
from tkinter import ttk
import time
from Modules.GUI.settings import *


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
        self.configure(background=BACKGROUND_COLOR)
        self.title("Soccer Field GUI:")
        # put a picture on the window background
        self.square_x = WINDOW_SQUARE_X
        self.square_y = WINDOW_SQUARE_Y
        self.x = WINDOW_X
        self.y = WINDOW_Y
        self.canvas_distance = {}
        self.entry_distance_labels = {}
        self.mask_dictionary = {}

        self.E_value = 0
        self.N_value = 0
        self.Radius_value = 0
        self.square_image_1 = None
        self.state("zoomed")
        self.resizable(True, True)
        self.create_widgets()
        # self.add_background_gif()

    def init_with_values(self, E="698812", N="3620547", Radius="0.2"):
        self.E_entry.insert(0, E)
        self.N_entry.insert(0, N)
        self.Radius_entry.insert(0, Radius)

    def add_E_cell(self):
        self.E = tk.Label(self, text="E: ")
        self.E.pack()
        self.E.place(relx=E_LABEL_LOCATION[0], rely=E_LABEL_LOCATION[1], anchor=tk.CENTER)
        self.E.config(font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        # add entry image
        self.cell_image = Image.open(cell_path)
        self.cell_image = self.cell_image.resize((CELL_WIDTH, CELL_HEIGHT), Image.ANTIALIAS)
        self.cell_image = ImageTk.PhotoImage(self.cell_image)
        cell_label = tk.Label(self, image=self.cell_image, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        cell_label.place(relx=E_ENTRY_LOCATION[0], rely=E_ENTRY_LOCATION[1], anchor=tk.CENTER)
        self.E_entry = tk.Entry(self)
        self.E_entry.pack()
        self.E_entry.place(relx=E_ENTRY_LOCATION[0], rely=E_ENTRY_LOCATION[1], anchor=tk.CENTER)

        self.E_entry.config(width=ENTRY_WIDTH - 50, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, font=FONT,
                            justify=tk.CENTER, bd=0, highlightthickness=0)

    def add_N_cell(self):
        # add label for entry it
        self.N = tk.Label(self, text="N: ")
        self.N.pack()
        self.N.place(relx=N_LABEL_LOCATION[0], rely=N_LABEL_LOCATION[1], anchor=tk.CENTER)
        self.N.config(font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        # add entry image
        self.cell_image_N = Image.open(cell_path)
        self.cell_image_N = self.cell_image_N.resize((CELL_WIDTH, CELL_HEIGHT), Image.ANTIALIAS)
        self.cell_image_N = ImageTk.PhotoImage(self.cell_image_N)
        cell_label = tk.Label(self, image=self.cell_image_N, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        cell_label.place(relx=N_ENTRY_LOCATION[0], rely=N_ENTRY_LOCATION[1], anchor=tk.CENTER)
        # add entry
        self.N_entry = tk.Entry(self)
        self.N_entry.pack()
        self.N_entry.place(relx=N_ENTRY_LOCATION[0], rely=N_ENTRY_LOCATION[1], anchor=tk.CENTER)
        self.N_entry.config(width=ENTRY_WIDTH - 50, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, font=FONT,
                            justify=tk.CENTER, bd=0, highlightthickness=0)

    def add_R_cell(self):
        self.Radius = tk.Label(self, text="Radius in km: ")
        self.Radius.pack()
        self.Radius.place(relx=R_LABEL_LOCATION[0], rely=R_LABEL_LOCATION[1], anchor=tk.CENTER)
        self.Radius.config(font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        # add entry image
        self.cell_image_R = Image.open(cell_path)
        self.cell_image_R = self.cell_image_R.resize((CELL_WIDTH, CELL_HEIGHT), Image.ANTIALIAS)
        self.cell_image_R = ImageTk.PhotoImage(self.cell_image_R)
        cell_label = tk.Label(self, image=self.cell_image_R, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        cell_label.place(relx=R_ENTRY_LOCATION[0], rely=R_ENTRY_LOCATION[1], anchor=tk.CENTER)
        # add entry
        self.Radius_entry = tk.Entry(self)
        self.Radius_entry.pack()
        self.Radius_entry.place(relx=R_ENTRY_LOCATION[0], rely=R_ENTRY_LOCATION[1], anchor=tk.CENTER)
        self.Radius_entry.config(width=ENTRY_WIDTH - 50, background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR,
                                 font=FONT,
                                 justify=tk.CENTER, bd=0, highlightthickness=0)

    def create_inputs_cells(self):
        self.add_E_cell()

        self.add_N_cell()
        self.add_R_cell()

    def create_widgets(self):
        # place the buttons on the window with a nice layout
        # add an entry for entering, E, N, and S, insert the entry values into the search function
        self.create_inputs_cells()
        # inserting the entry values into the search function
        self.add_search_button()
        self.add_progressbar()
        self.create_images_and_canvas()
        self.add_original_image(self.original_image_array)
        self.add_result_image(self.result_image_array)
        self.bind_keys()
        self.create_slider()
        # self.create_type_label()
        # self.change_type_button()
        self.add_masks_check_points()

        self.init_with_values()

        # Define a function to set the start point of the line

    def add_masks_check_points(self):
        # check points are the boxes that are checked in the check boxes
        self.trees_check_point = tk.IntVar()
        self.trees_check_point.set(1)
        self.trees_check_box = tk.Checkbutton(self, text="Trees", variable=self.trees_check_point,
                                              command=self.check_box_changed)
        self.trees_check_box.pack()
        self.trees_check_box.place(relx=TREES_CHECK_BOX_LOCATION[0], rely=TREES_CHECK_BOX_LOCATION[1], anchor=tk.CENTER)
        self.trees_check_box.config(font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        self.buildings_check_point = tk.IntVar()
        self.buildings_check_point.set(0)
        self.buildings_check_box = tk.Checkbutton(self, text="Buildings", variable=self.buildings_check_point,
                                                  command=self.check_box_changed)
        self.buildings_check_box.pack()
        self.buildings_check_box.place(relx=BUILDINGS_CHECK_BOX_LOCATION[0], rely=BUILDINGS_CHECK_BOX_LOCATION[1],
                                       anchor=tk.CENTER)
        self.buildings_check_box.config(font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        self.electricity_check_point = tk.IntVar()
        self.electricity_check_point.set(0)
        self.electricity_check_box = tk.Checkbutton(self, text="Electricity", variable=self.electricity_check_point,
                                                    command=self.check_box_changed)
        self.electricity_check_box.pack()
        self.electricity_check_box.place(relx=ELECTRICITY_CHECK_BOX_LOCATION[0],
                                         rely=ELECTRICITY_CHECK_BOX_LOCATION[1], anchor=tk.CENTER)
        self.electricity_check_box.config(font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)
        self.slope_check_point = tk.IntVar()
        self.slope_check_point.set(1)
        self.slope_check_box = tk.Checkbutton(self, text="Slope", variable=self.slope_check_point,
                                              command=self.check_box_changed)
        self.slope_check_box.pack()
        self.slope_check_box.place(relx=SLOPES_CHECK_BOX_LOCATION[0], rely=SLOPES_CHECK_BOX_LOCATION[1],
                                   anchor=tk.CENTER)
        self.slope_check_box.config(font=FONT, foreground=FOREGROUND_COLOR, background=BACKGROUND_COLOR)

    def check_box_changed(self):
        key_for_check_point = ""
        if self.buildings_check_point.get() == 1:
            key_for_check_point += "Buildings"
        if self.electricity_check_point.get() == 1:
            key_for_check_point += "&Electricity"
        if self.slope_check_point.get() == 1:
            key_for_check_point += "&Slopes"
        if self.trees_check_point.get() == 1:
            key_for_check_point += "&Trees"
        if key_for_check_point[0] == "&":
            key_for_check_point = key_for_check_point[1:]
        self.add_original_image(self.saved_og_image)
        self.add_result_image(self.mask_dictionary[key_for_check_point])
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
        float_R = 1 if float(self.get_Radius_value()) == 0 else float(self.get_Radius_value())
        self.distance = 2 * self.distance * float_R * 1000 / CANVAS_WIDTH
        self.distance = round(self.distance, 2)
        self.add_entry_distance()

    def search(self):
        # get the entry values
        # estimate runtime

        # self.add_background_gif()
        self.update_progressbar(0)
        self.E_value = self.E_entry.get()
        self.N_value = self.N_entry.get()
        self.Radius_value = self.Radius_entry.get()
        coordinates = (int(self.E_value), int(self.N_value), 36, "N")
        # need to add logs of this in main
        print(coordinates, self.Radius_value)
        # run the function
        t = threading.Thread(target=self.run_process, args=(coordinates,))
        # image, total_mask = get_viable_landing_in_radius(coordinates, float(self.Radius_value), self)
        t.start()
        progress_thread = threading.Thread(target=self.run_progressbar())
        progress_thread.start()

    def run_process(self, coordinates):
        image, total_mask = get_viable_landing_in_radius(coordinates, float(self.Radius_value), self)
        self.add_original_image(image)
        self.mask_dictionary = total_mask
        print(total_mask.keys())
        print(total_mask)
        self.add_result_image(total_mask["Slopes&Trees"])

        # self.background_label.destroy()
        self.update_transparency(50)
        self.transparency_slider.set(50)

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
            float_R = 1 if float(self.get_Radius_value()) == 0 else float(self.get_Radius_value())
            self.distance = 2 * self.distance * float_R * 1000 / CANVAS_WIDTH
            self.distance = round(self.distance, 2)
            self.add_entry_distance()
            # self.entry_distance_labels[self.line].config(text=DISTANCE_STR_FORMAT(self.distance))

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
            # place the entry distance label on the canvas above the line that in position (x1,y1) and (x2,y2)
            # (x1,y1) is self.canvas_distance[self.line][0], self.canvas_distance[self.line][1]
            # (x2,y2) is self.canvas_distance[self.line][2], self.canvas_distance[self.line][3]
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

    def create_images_and_canvas(self):
        self.original_image = Image.open(ORIGINAL_IMAGE_PATH)
        self.result_image = Image.open(RESULT_IMAGE_PATH)
        # # make self.original_image and self.result_image an array of the image
        self.original_image_array = np.array(self.original_image)
        self.result_image_array = np.array(self.result_image)
        self.square_image_array = np.array(Image.open(HELICOPTER_IMAGE_PATH))
        # add the original image and the result image to the window
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

    def bind_keys(self):
        self.line = -111
        self.bind("<Left>", self.left_key)
        self.bind("<Right>", self.right_key)
        self.bind("<Up>", self.up_key)
        self.bind("<Down>", self.down_key)
        self.bind(ROTATION_KEY, self.rotate_square_image_clockwise)
        # Bind the left mouse button to the start function and the left mouse motion to the draw function
        self.canvas.bind("<Button-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<Button-3>", self.delete_line)

    def rotate_square_image_clockwise(self, event):
        # rotate the square image 45 degrees clockwise
        self.square_x, self.square_y = self.square_y, self.square_x
        self.square_image_1 = Image.fromarray(cv2.cvtColor(self.square_image_array, cv2.COLOR_BGR2RGB)).resize(
            (self.square_x, self.square_y))
        self.square_image = ImageTk.PhotoImage(self.square_image_1)
        self.canvas.itemconfig(self.square_image_canvas, image=self.square_image)

    def left_key(self, event):
        # dont let the square image go out of the canvas\
        c1 = self.canvas.coords(self.square_image_canvas)
        if c1[0] > 0:
            self.canvas.move(self.square_image_canvas, -1, 0)

    def right_key(self, event):
        # dont let the square image go out of the canvas
        c1 = self.canvas.coords(self.square_image_canvas)
        if c1[0] + self.square_x < self.x:
            self.canvas.move(self.square_image_canvas, 1, 0)

    def up_key(self, event):
        # dont let the square image go out of the canvas
        c1 = self.canvas.coords(self.square_image_canvas)
        if c1[1] > 0:
            self.canvas.move(self.square_image_canvas, 0, -1)

    def down_key(self, event):
        # dont let the square image go out of the canvas
        # get the pixel coordinates of the square image
        c1 = self.canvas.coords(self.square_image_canvas)
        if c1[1] + 30 + 2 * self.square_y < self.y:
            self.canvas.move(self.square_image_canvas, 0, 1)

    def add_square_image(self):
        """
        get the square image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 200
        :param image: the square image
        :return:
        """
        self.square_image_1 = Image.fromarray(cv2.cvtColor(self.square_image_array, cv2.COLOR_BGR2RGB)).resize(
            (self.square_x, self.square_y))
        self.square_image = ImageTk.PhotoImage(self.square_image_1)
        self.square_image_canvas = self.canvas.create_image(0, 0, image=self.square_image, anchor=tk.NW)

    def add_original_image(self, image):
        """
        get the original image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 200
        :param image: the original image
        :return:
        """
        self.saved_og_image = image
        self.original_image_1 = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).resize((self.x, self.y))
        self.original_image = ImageTk.PhotoImage(self.original_image_1)
        self.canvas.create_image(0, 0, image=self.original_image, anchor=tk.NW)

    def add_result_image(self, image):
        """
        get the result image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 420
        :param image: the result image
        :return:
        """
        if self.mask_dictionary == {}:
            self.mask_dictionary = {k : image for k in MASKS_KEYS}
        self.result_image_1 = Image.fromarray(image).resize((self.x, self.y))
        self.result_image_1 = self.result_image_1.convert(mode='RGB')
        self.result_image = ImageTk.PhotoImage(self.result_image_1)

        self.result_image_canvas = self.canvas.create_image(0, 0, image=self.result_image, anchor=tk.NW)
        # self.add_square_image()

    def make_zoom_in(self):
        # Set the initial viewport size
        VIEWPORT_WIDTH = CANVAS_WIDTH
        VIEWPORT_HEIGHT = CANVAS_HEIGHT
        # Set the initial viewport position

        # Display the image on the canvas
        img = self.result_image_1
        image_item = self.result_image_canvas

        # Define a function to update the viewport and redraw the image
        def update_viewport():
            # Calculate the coordinates of the viewport
            x1 = VIEWPORT_X
            y1 = VIEWPORT_Y
            x2 = x1 + VIEWPORT_WIDTH
            y2 = y1 + VIEWPORT_HEIGHT

            # Set the canvas viewport
            self.canvas.configure(scrollregion=(0, 0, img.width, img.height), width=VIEWPORT_WIDTH,
                                  height=VIEWPORT_HEIGHT)
            self.canvas.xview_moveto(x1 / img.width)
            self.canvas.yview_moveto(y1 / img.height)

            # Redraw the image in the viewport
            cropped_img = img.crop((x1, y1, x2, y2))
            cropped_tk = ImageTk.PhotoImage(cropped_img)
            self.canvas.itemconfig(image_item, image=cropped_tk)

        # Define a function to zoom in or out on the image
        def zoom(event):
            global VIEWPORT_X, VIEWPORT_Y, VIEWPORT_WIDTH, VIEWPORT_HEIGHT
            if event.delta < 0:
                # Zoom out
                VIEWPORT_X -= VIEWPORT_WIDTH // 4  # Decrease the viewport size by 25%
                VIEWPORT_Y -= VIEWPORT_HEIGHT // 4
                VIEWPORT_WIDTH *= 2
                VIEWPORT_HEIGHT *= 2
            else:
                # Zoom in
                VIEWPORT_X += VIEWPORT_WIDTH // 4  # Increase the viewport size by 25%
                VIEWPORT_Y += VIEWPORT_HEIGHT // 4
                VIEWPORT_WIDTH //= 2
                VIEWPORT_HEIGHT //= 2
            update_viewport()

        # Bind the function to a mouse wheel event
        self.canvas.bind("<MouseWheel>", zoom)

    def add_progressbar(self):

        # define the style
        pb_style = ttk.Style()
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        pb_style.theme_use("default")
        pb_style.layout('text.Horizontal.TProgressbar',
                        [('Horizontal.Progressbar.trough',
                          {'children': [('Horizontal.Progressbar.pbar',
                                         {'side': 'left', 'sticky': 'ns'})],
                           'sticky': 'nswe'}),
                         ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
        pb_style.configure('text.Horizontal.TProgressbar', anchor='center',
                           background=SECOND_BACKGROUND_COLOR, )
        self.progressbar = ttk.Progressbar(self, orient="horizontal", length=PROGRESSBAR_LENGTH, mode="determinate",
                                           style="text.Horizontal.TProgressbar")
        self.progressbar.place(relx=POGRESSBAR_LOCATION[0], rely=POGRESSBAR_LOCATION[1], anchor=tk.CENTER)
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        self.progressbar_label = tk.Label(self, text="0%", font=FONT, foreground=FOREGROUND_COLOR,
                                          background=BACKGROUND_COLOR)
        self.progressbar_label.place(relx=POGRESSBAR_LOCATION_LABEL[0], rely=POGRESSBAR_LOCATION_LABEL[1],
                                     anchor=tk.CENTER)

    def update_progressbar(self, value):
        self.progressbar_label.config(text=f"{value}%")
        self.progressbar["value"] = value
        self.progressbar.update()

    def run_progressbar(self):
        time_for_km_area = 100  # sec
        self.time_for_iteration = (time_for_km_area * (2 * (float(self.Radius_value)) ** 2) / 100)
        while self.progressbar['value'] < 99:
            current_value = self.progressbar['value']
            self.update_progressbar(current_value + 1)
            print(self.time_for_iteration, self.progressbar['value'])
            time.sleep(self.time_for_iteration)  # 70 sec per km^2, total time = 0.1 * (2R)^2, itreatiiom time=
        else:
            print('Progresbar complete!')

    def set_time_for_iteration(self, slopy):
        time_for_flat_km_area = 190
        new_area = (2 * (float(self.Radius_value)) ** 2) * (slopy / 100)
        self.time_for_iteration = new_area * time_for_flat_km_area / 100
        # self.time_for_iteration = ((time_for_flat_km_area * (2 * (float(self.Radius_value)) ** 2)) + (
        #         time_for_flat_km_area * (slopy / 100) ** 3)) / (2 * 100)

    def add_background_gif(self):
        # TO DO:
        # fix bug with the gif
        # Open the GIF image using PIL
        image = Image.open(logo_path_gif)  # Replace "animation.gif" with the filename or file path of your GIF image
        # chagne image background to white
        # Create a list to store individual frames of the GIF image
        frames = []
        # Loop through each frame in the GIF image and append it to the frames list
        for frame in ImageSequence.Iterator(image):
            resized_frame = frame.resize((self.x, self.y))
            frames.append(ImageTk.PhotoImage(resized_frame))
            # add to canves
        # Create a Label widget to display the animated GIF
        self.background_label = tk.Label(self.canvas, image=frames[0], width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.background_label.pack()

        # self.canvas.create_window(0, 0, window=self.background_label, anchor=tk.NW)
        # Function to update the Label with the next frame of the animated GIF
        def update_label(frame_idx):
            self.background_label.config(image=frames[frame_idx], width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
            self.after(100, update_label, (frame_idx + 1) % len(frames))

        # Start displaying the animated GIF
        update_label(0)

    def add_search_button(self):
        # add image
        self.search_image = Image.open(search_path)
        self.search_image = self.search_image.resize((SEARCH_BUTTON_WIDTH, SEARCH_BUTTON_HEIGHT))
        self.search_image = ImageTk.PhotoImage(self.search_image)
        self.search_button = tk.Button(self, image=self.search_image, command=self.search, bg=BACKGROUND_COLOR, bd=0,
                                       highlightthickness=0, activebackground=BACKGROUND_COLOR)
        # self.search_button = tk.Button(self, text="חפש", command=self.search)
        self.search_button.pack()
        self.search_button.place(relx=SEARCH_BUTTON_LOCATION[0], rely=SEARCH_BUTTON_LOCATION[1], anchor=tk.CENTER)
        self.search_button.config(background=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, borderwidth=0)

    def create_slider(self):
        self.transparency_slider = tk.Scale(self, from_=0, to=100, orient=tk.VERTICAL, length=CANVAS_HEIGHT,
                                            width=SLIDER_WIDTH,
                                            sliderlength=SLIDER_LENGTH,
                                            background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, )
        self.transparency_slider.set(100)
        self.transparency_slider.pack()
        self.transparency_slider.place(relx=SLIDER_LOCATION[0], rely=SLIDER_LOCATION[1], anchor=tk.CENTER)
        # Call the update_transparency function when the slider is moved
        self.transparency_slider.config(command=self.update_transparency)
        self.update_transparency(100)

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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
    print("Done!")
