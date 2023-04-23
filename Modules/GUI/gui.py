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

# Get the directory path of the current file (gui.py)
dir_path = os.path.dirname(os.path.realpath(__file__))

# Construct the absolute path of logo.png
logo_path_gif = os.path.join(dir_path, 'LOGO.gif')
logo_path = os.path.join(dir_path, 'logo.png')
# Construct the absolute path of background.png
pnotnp_path = os.path.join(dir_path, 'PNOTNP.jpg')
# Construct the absolute path of background.png
pnp_path = os.path.join(dir_path, 'PNP.jpg')
# Construct the absolute path of background.png
ws_path = os.path.join(dir_path, 'yasor.jpg')
# Construct the absolute path of the original image and result image
original_image_path = logo_path
result_image_path = pnp_path
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
wx, wy, wsx, wsy = 500, 500, 50, 20
canvas_location = (0.5, 0.55)
canvas_width, canvas_highet = wx, wy - 50
canvas_highlight_color = 'red'
alpha_func = lambda val: int(float(val) * 255 / 100)
rotate_key = "1"
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
        self.create_type_label()
        self.change_type_button()

    def create_images_and_canvas(self):
        self.original_image = Image.open(original_image_path)
        self.result_image = Image.open(result_image_path)
        # # make self.original_image and self.result_image an array of the image
        self.original_image_array = np.array(self.original_image)
        self.result_image_array = np.array(self.result_image)
        self.square_image_array = np.array(Image.open(ws_path))
        # add the original image and the result image to the window
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_highet, bg="white", highlightcolor=canvas_highlight_color)
        self.canvas.place(relx=canvas_location[0], rely=canvas_location[1], anchor=tk.CENTER)

    def update_transparency(self, val):
        alpha = alpha_func(val)
        cop = self.result_image_1.copy()
        cop.putalpha(alpha)
        alpha_image = ImageTk.PhotoImage(cop)
        self.canvas.itemconfig(self.result_image_canvas, image=alpha_image)
        self.canvas.image = alpha_image

    def bind_keys(self):
        self.bind("<Left>", self.left_key)
        self.bind("<Right>", self.right_key)
        self.bind("<Up>", self.up_key)
        self.bind("<Down>", self.down_key)
        self.bind(rotate_key, self.rotate_square_image_clockwise)
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
        self.result_image_1 = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).resize((self.x, self.y))
        self.result_image = ImageTk.PhotoImage(self.result_image_1)
        self.result_image_canvas = self.canvas.create_image(0, 0, image=self.result_image, anchor=tk.NW)
        self.add_square_image()

    def get_E_value(self):
        return self.E_value

    def get_N_value(self):
        return self.N_value

    def get_Radius_value(self):
        return self.Radius_value

    def add_progressbar(self):
        self.progressbar = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate",
                                           style="lightblue.Horizontal.TProgressbar")
        self.progressbar.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0
        self.progressbar_label = tk.Label(self, text="0%", font=FONT, foreground="black", background=background_color)
        self.progressbar_label.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

    def update_progressbar(self, value):
        self.progressbar_label.config(text=f"{value}%")
        self.progressbar["value"] = value
        self.progressbar.update()

    def add_background_gif(self):
        # Open the GIF image using PIL
        image = Image.open(logo_path_gif)  # Replace "animation.gif" with the filename or file path of your GIF image
        # Create a list to store individual frames of the GIF image
        frames = []
        # Loop through each frame in the GIF image and append it to the frames list
        for frame in ImageSequence.Iterator(image):
            resized_frame = frame.resize((150, 150))
            frames.append(ImageTk.PhotoImage(resized_frame))
        # Create a Label widget to display the animated GIF
        self.background_label = tk.Label(self)
        self.background_label.place(x=1800, y=300, anchor=tk.CENTER)
        self.background_label.pack()

        # self.background_label.resize(100, 100)
        # Function to update the Label with the next frame of the animated GIF
        def update_label(frame_idx):
            self.background_label.config(image=frames[frame_idx])
            self.after(100, update_label, (frame_idx + 1) % len(frames))

        # Start displaying the animated GIF
        update_label(0)

    def add_search_button(self):
        self.search_button = tk.Button(self, text="חפש", command=self.search)
        self.search_button.pack()
        self.search_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        self.search_button.config(background=second_background_color, foreground="black", font=FONT)

    def create_slider(self):
        transparency_slider = tk.Scale(self, from_=0, to=100, orient=tk.VERTICAL, length=450, width=15, sliderlength=20,
                                       background=background_color, foreground="black", )
        transparency_slider.set(100)
        transparency_slider.pack()
        transparency_slider.place(relx=0.32, rely=0.55, anchor=tk.CENTER)
        # Call the update_transparency function when the slider is moved
        transparency_slider.config(command=self.update_transparency)
        self.update_transparency(100)


    def change_type_button(self):
        self.size_button = tk.Button(self, text="Change Type", command=self.update_size)
        self.size_button.pack()
        self.size_button.place(relx=0.2, rely=0.7, anchor=tk.CENTER)
        self.size_button.config(background=second_background_color, foreground="black", font=FONT)
    def create_type_label(self):
        self.type_label = tk.Label(self, text="יסעור", font=FONT, foreground="black", background=second_background_color)
        self.type_label.place(relx=0.2, rely=0.6, anchor=tk.CENTER)

    def update_size(self):
        # change the size of the square image to fit the helicopter type
        if self.type_label["text"] == "יסעור":
            self.type_label["text"]="ינשוף"
            self.sx = 50
            self.sy = 20
        elif self.type_label["text"] == "ינשוף":
            self.type_label["text"]="יסעור"
            self.sx = 70
            self.sy = 200
        self.add_square_image()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
