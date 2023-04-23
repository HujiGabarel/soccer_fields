import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import numpy as np
import math

from Modules.Main.Main import get_viable_landing_in_radius
import cv2
import threading
import os
from PIL import Image
from tkinter import ttk
from tkVideoPlayer import TkinterVideo

# Get the directory path of the current file (gui.py)
dir_path = os.path.dirname(os.path.realpath(__file__))

# Construct the absolute path of logo.png
logo_path_gif = os.path.join(dir_path, 'logo.gif')
logo_path = os.path.join(dir_path, 'logo.png')
# Construct the absolute path of background.png
pnotnp_path = os.path.join(dir_path, 'PNOTNP.jpg')
# Construct the absolute path of background.png
pnp_path = os.path.join(dir_path, 'PNP.jpg')
# Construct the absolute path of background.png
ws_path = os.path.join(dir_path, 'yasor.jpg')
# Construct the absolute path of the original image and result image
original_image_path = logo_path
result_image_path = logo_path
FONT = ('Helvetica', 16, "bold")
background_color = 'white'
second_background_color = 'light blue'
entry_width = 20
E_label_location = (0.41, 0.05)
E_entry_location = (0.5, 0.05)
N_label_location = (0.41, 0.1)
N_entry_location = (0.5, 0.1)
R_label_location = (0.375, 0.15)
R_entry_location = (0.5, 0.15)
distance_entry_location = (0.8, 0.3)
wx, wy, wsx, wsy = 500, 500, 50, 20
canvas_location = (0.5, 0.55)
CANVAS_WIDTH, CANVAS_HEIGHT = 500, 500
SLIDER_WIDTH, SLIDER_LENGTH = 15, 20
POGRESSBAR_WIDTH, PROGRESSBAR_LENGTH = 15, 200
POGRESSBAR_LOCATION = (0.5, 0.93)
POGRESSBAR_LOCATION_LABEL = (0.5, 0.89)
canvas_highlight_color = 'red'
alpha_func = lambda val: int(float(val) * 255 / 100)
rotate_key = "1"
distance_str_format = lambda x: f"Distance: {x} m"
viewport_x = 0
viewport_y = 0
viewport_width = CANVAS_WIDTH
viewport_height = CANVAS_HEIGHT
start_x, start_y = None, None
end_x, end_y = None, None


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(background=background_color)
        self.title("Soccer Field GUI:")
        # put a picture on the window background
        self.sx = wsx
        self.sy = wsy
        self.x = wx
        self.y = wy
        self.square_image_1 = None
        self.state("zoomed")
        # self.add_background_gif()
        self.resizable(True, True)
        self.create_widgets()

    def create_inputs_cells(self):
        self.E = tk.Label(self, text="E: ")
        self.E.pack()
        self.E_entry = tk.Entry(self)
        self.E_entry.config(background=second_background_color, foreground="black", font=FONT, justify=tk.CENTER)
        self.E_entry.pack()
        self.N = tk.Label(self, text="N: ")
        self.N.pack()
        self.N_entry = tk.Entry(self)
        self.N_entry.config(background=second_background_color, foreground="black", font=FONT, justify=tk.CENTER)
        self.N_entry.pack()
        self.Radius = tk.Label(self, text="Radius in km: ")
        self.Radius.pack()
        self.Radius_entry = tk.Entry(self)
        self.Radius_entry.config(background=second_background_color, foreground="black", font=FONT, justify=tk.CENTER)
        self.Radius_entry.pack()

        self.E.place(relx=E_label_location[0], rely=E_label_location[1], anchor=tk.CENTER)
        self.E.config(font=FONT, foreground="black", background=background_color)
        self.E_entry.place(relx=E_entry_location[0], rely=E_entry_location[1], anchor=tk.CENTER)
        self.E_entry.config(width=entry_width)
        self.N.place(relx=N_label_location[0], rely=N_label_location[1], anchor=tk.CENTER)
        self.N.config(font=FONT, foreground="black", background=background_color)
        self.N_entry.place(relx=N_entry_location[0], rely=N_entry_location[1], anchor=tk.CENTER)
        self.N_entry.config(width=entry_width)
        self.Radius.place(relx=R_label_location[0], rely=R_label_location[1], anchor=tk.CENTER)
        self.Radius.config(font=FONT, foreground="black", background=background_color)
        self.Radius_entry.place(relx=R_entry_location[0], rely=R_entry_location[1], anchor=tk.CENTER)
        self.Radius_entry.config(width=entry_width)

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
        self.init_with_values()
        self.add_entry_distance()
        # self.make_zoom_in()

        # Define a function to set the start point of the line

    def start(self, event):
        global start_x, start_y
        start_x, start_y = event.x, event.y

        # Define a function to update the end point of the line and draw it

    def draw(self, event):
        global start_x, start_y, end_x, end_y
        if start_x and start_y:
            end_x, end_y = event.x, event.y
            if self.line != -111:
                # move the line to the new position
                self.canvas.coords(self.line, start_x, start_y, end_x, end_y)
            else:
                self.line = self.canvas.create_line(start_x, start_y, end_x, end_y, width=2, fill="black", smooth=True)
            # calculate the distance between the two points
            self.distance = math.sqrt((start_x - end_x) ** 2 + (start_y - end_y) ** 2)
            self.distance = 2*self.distance * float(self.get_Radius_value()) * 1000 / CANVAS_WIDTH
            self.distance = round(self.distance, 2)
            self.entry_distance.config(text=distance_str_format(self.distance))

    def init_with_values(self, E="698812", N="3620547", Radius="0.1"):
        self.E_entry.insert(0, E)
        self.N_entry.insert(0, N)
        self.Radius_entry.insert(0, Radius)

    def create_images_and_canvas(self):
        self.original_image = Image.open(original_image_path)
        self.result_image = Image.open(result_image_path)
        # # make self.original_image and self.result_image an array of the image
        self.original_image_array = np.array(self.original_image)
        self.result_image_array = np.array(self.result_image)
        self.square_image_array = np.array(Image.open(ws_path))
        # add the original image and the result image to the window
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white",
                                highlightcolor=canvas_highlight_color)
        self.canvas.place(relx=canvas_location[0], rely=canvas_location[1], anchor=tk.CENTER)

    def add_entry_distance(self):
        self.entry_distance = tk.Label(self, width=entry_width, justify=tk.CENTER, font=FONT,
                                       bg=second_background_color, fg="black")
        self.entry_distance.place(relx=distance_entry_location[0], rely=distance_entry_location[1], anchor=tk.CENTER)
        self.entry_distance.config(text="Distance: ")

    def update_transparency(self, val):
        alpha = alpha_func(val)
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
        self.bind(rotate_key, self.rotate_square_image_clockwise)
        # Bind the left mouse button to the start function and the left mouse motion to the draw function
        self.canvas.bind("<Button-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.draw)

    def rotate_square_image_clockwise(self, event):
        # rotate the square image 45 degrees clockwise
        self.sx, self.sy = self.sy, self.sx
        self.square_image_1 = Image.fromarray(cv2.cvtColor(self.square_image_array, cv2.COLOR_BGR2RGB)).resize(
            (self.sx, self.sy))
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
        if c1[0] + self.sx < self.x:
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
        if c1[1] + 30 + 2 * self.sy < self.y:
            self.canvas.move(self.square_image_canvas, 0, 1)

    def search(self):
        # get the entry values
        self.add_background_gif()
        self.update_progressbar(0)
        self.E_value = self.E_entry.get()
        self.N_value = self.N_entry.get()
        self.Radius_value = self.Radius_entry.get()
        coordinates = (int(self.E_value), int(self.N_value), 36, "N")
        print(coordinates, self.Radius_value)
        # run the function
        t = threading.Thread(target=self.run_process, args=(coordinates,))
        # image, total_mask = get_viable_landing_in_radius(coordinates, float(self.Radius_value), self)
        t.start()

    def run_process(self, coordinates):
        image, total_mask = get_viable_landing_in_radius(coordinates, float(self.Radius_value), self)
        self.add_original_image(image)
        self.add_result_image(total_mask)
        self.background_label.destroy()
        self.update_transparency(50)
        self.transparency_slider.set(50)

    def add_square_image(self):
        """
        get the square image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 200
        :param image: the square image
        :return:
        """
        self.square_image_1 = Image.fromarray(cv2.cvtColor(self.square_image_array, cv2.COLOR_BGR2RGB)).resize(
            (self.sx, self.sy))
        self.square_image = ImageTk.PhotoImage(self.square_image_1)
        self.square_image_canvas = self.canvas.create_image(0, 0, image=self.square_image, anchor=tk.NW)

    def add_original_image(self, image):
        """
        get the original image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 200
        :param image: the original image
        :return:
        """
        self.original_image_1 = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).resize((self.x, self.y))
        self.original_image = ImageTk.PhotoImage(self.original_image_1)
        self.canvas.create_image(0, 0, image=self.original_image, anchor=tk.NW)

    def add_result_image(self, image):
        """
        get the result image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 420
        :param image: the result image
        :return:
        """
        self.result_image_1 = Image.fromarray(image).resize((self.x, self.y))
        self.result_image_1 = self.result_image_1.convert(mode='RGB')
        self.result_image = ImageTk.PhotoImage(self.result_image_1)
        self.result_image_canvas = self.canvas.create_image(0, 0, image=self.result_image, anchor=tk.NW)
        # self.add_square_image()

    def get_E_value(self):
        return self.E_value

    def get_N_value(self):
        return self.N_value

    def get_Radius_value(self):
        return self.Radius_value

    def make_zoom_in(self):
        # Set the initial viewport size
        viewport_width = CANVAS_WIDTH
        viewport_height = CANVAS_HEIGHT
        # Set the initial viewport position

        # Display the image on the canvas
        img = self.result_image_1
        image_item = self.result_image_canvas

        # Define a function to update the viewport and redraw the image
        def update_viewport():
            # Calculate the coordinates of the viewport
            x1 = viewport_x
            y1 = viewport_y
            x2 = x1 + viewport_width
            y2 = y1 + viewport_height

            # Set the canvas viewport
            self.canvas.configure(scrollregion=(0, 0, img.width, img.height), width=viewport_width,
                                  height=viewport_height)
            self.canvas.xview_moveto(x1 / img.width)
            self.canvas.yview_moveto(y1 / img.height)

            # Redraw the image in the viewport
            cropped_img = img.crop((x1, y1, x2, y2))
            cropped_tk = ImageTk.PhotoImage(cropped_img)
            self.canvas.itemconfig(image_item, image=cropped_tk)

        # Define a function to zoom in or out on the image
        def zoom(event):
            global viewport_x, viewport_y, viewport_width, viewport_height
            if event.delta < 0:
                # Zoom out
                viewport_x -= viewport_width // 4  # Decrease the viewport size by 25%
                viewport_y -= viewport_height // 4
                viewport_width *= 2
                viewport_height *= 2
            else:
                # Zoom in
                viewport_x += viewport_width // 4  # Increase the viewport size by 25%
                viewport_y += viewport_height // 4
                viewport_width //= 2
                viewport_height //= 2
            update_viewport()

        # Bind the function to a mouse wheel event
        self.canvas.bind("<MouseWheel>", zoom)

    def add_progressbar(self):
        self.progressbar = ttk.Progressbar(self, orient="horizontal", length=PROGRESSBAR_LENGTH, mode="determinate",
                                           style="lightblue.Horizontal.TProgressbar")
        self.progressbar.place(relx=POGRESSBAR_LOCATION[0], rely=POGRESSBAR_LOCATION[1], anchor=tk.CENTER)
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        self.progressbar_label = tk.Label(self, text="0%", font=FONT, foreground="black", background=background_color)
        self.progressbar_label.place(relx=POGRESSBAR_LOCATION_LABEL[0], rely=POGRESSBAR_LOCATION_LABEL[1], anchor=tk.CENTER)

    def update_progressbar(self, value):
        self.progressbar_label.config(text=f"{value}%")
        self.progressbar["value"] = value
        self.progressbar.update()

    def add_background_gif(self):
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
        self.search_button = tk.Button(self, text="חפש", command=self.search)
        self.search_button.pack()
        self.search_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        self.search_button.config(background=second_background_color, foreground="black", font=FONT)

    def create_slider(self):
        self.transparency_slider = tk.Scale(self, from_=0, to=100, orient=tk.VERTICAL, length=CANVAS_HEIGHT,
                                            width=SLIDER_WIDTH,
                                            sliderlength=SLIDER_LENGTH,
                                            background=background_color, foreground="black", )
        self.transparency_slider.set(100)
        self.transparency_slider.pack()
        self.transparency_slider.place(relx=0.32, rely=0.55, anchor=tk.CENTER)
        # Call the update_transparency function when the slider is moved
        self.transparency_slider.config(command=self.update_transparency)
        self.update_transparency(100)

    def change_type_button(self):
        self.size_button = tk.Button(self, text="Change Type", command=self.update_size)
        self.size_button.pack()
        self.size_button.place(relx=0.2, rely=0.7, anchor=tk.CENTER)
        self.size_button.config(background=second_background_color, foreground="black", font=FONT)

    def create_type_label(self):
        self.type_label = tk.Label(self, text="יסעור", font=FONT, foreground="black",
                                   background=second_background_color)
        self.type_label.place(relx=0.2, rely=0.6, anchor=tk.CENTER)

    def update_size(self):
        # change the size of the square image to fit the helicopter type
        if self.type_label["text"] == "יסעור":
            self.type_label["text"] = "ינשוף"
            self.sx = 50
            self.sy = 20
        elif self.type_label["text"] == "ינשוף":
            self.type_label["text"] = "יסעור"
            self.sx = 70
            self.sy = 200
        self.add_square_image()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
