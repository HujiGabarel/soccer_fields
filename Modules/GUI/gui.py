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
pnotnp_path = os.path.join(dir_path, 'PNP.jpg')
# Construct the absolute path of background.png
pnp_path = os.path.join(dir_path, 'PNOTNP.jpg')
# Construct the absolute path of background.png
ws_path = os.path.join(dir_path, 'whitesquare.png')
FONT = ('Helvetica', 16, "bold")
background_color = 'white'
second_background_color = 'light blue'


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(background=background_color)
        self.search_button = None
        self.Radius_entry = None
        self.Radius = None
        self.N_entry = None
        self.N = None
        self.E_entry = None
        self.E = None
        self.E_value = None
        self.N_value = None
        self.Radius_value = None
        self.title("Soccer Field GUI:")
        # put a picture on the window background
        self.x = 1000
        self.y = 1000
        self.sx = 50
        self.sy = 20
        flag = False
        if flag:
            self.geometry(f"{self.x}x{self.y}")
        else:
            # this is the size of the images original and result
            self.x = 500
            self.y = 500
            self.state("zoomed")
        picture_x_y = 150
        # self.add_background_gif()
        self.resizable(True, True)
        self.create_widgets()

    def create_widgets(self):
        # place the buttons on the window with a nice layout
        # add an entry for entering, E, N, and S, insert the entry values into the search function
        position = tk.CENTER
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

        # inserting the entry values into the search function
        self.search_button = tk.Button(self, text="חפש", command=self.search)
        # self.search_button = tk.Button(self, text="חפש", command=threading.Thread(target=self.do).start)
        self.search_button.pack()
        self.add_progressbar()
        labels = [self.E, self.N, self.Radius, self.E_entry, self.N_entry, self.Radius_entry, self.search_button]

        gap = 1.5
        entry_width = 20
        height = 10
        level = 1
        start_x = 800
        start_y = 20
        self.E.place(relx=0.41, rely=0.05, anchor=position)
        self.E.config(font=FONT, foreground="black", background=background_color)
        self.E_entry.place(relx=0.5, rely=0.05, anchor=position)
        self.E_entry.config(width=entry_width)
        self.N.place(relx=0.41, rely=0.1, anchor=position)
        self.N.config(font=FONT, foreground="black", background=background_color)
        self.N_entry.place(relx=0.5, rely=0.1, anchor=position)
        self.N_entry.config(width=entry_width)
        self.Radius.place(relx=0.375, rely=0.15, anchor=position)
        self.Radius.config(font=FONT, foreground="black", background=background_color)
        self.Radius_entry.place(relx=0.5, rely=0.15, anchor=position)
        self.Radius_entry.config(width=entry_width)
        self.search_button.place(relx=0.5, rely=0.2, anchor=position)
        self.search_button.config(background=second_background_color, foreground="black", font=FONT)
        self.original_image = Image.open(pnp_path)
        self.result_image = Image.open(pnotnp_path)
        # # make self.original_image and self.result_image an array of the image
        self.original_image_array = np.array(self.original_image)
        self.result_image_array = np.array(self.result_image)
        # add the original image and the result image to the window
        self.canvas = tk.Canvas(self, width=self.x * 3, height=self.y-50, bg="red")
        self.canvas.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

        self.add_original_image(self.original_image_array)

        self.add_result_image(self.result_image_array)
        #self.result_image = ImageTk.PhotoImage(
            #Image.fromarray(cv2.cvtColor(self.result_image_array, cv2.COLOR_BGR2RGB)).resize((self.x, self.y)))
        self.square_image_array = np.array(Image.open(ws_path))
        self.square_image = ImageTk.PhotoImage(
            Image.fromarray(cv2.cvtColor(self.square_image_array, cv2.COLOR_BGR2RGB)).resize((self.sx, self.sy)))
        # self.result_label = tk.Label(self.canvas, image=self.result_image)
        # self.result_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)

        # self.square_label = tk.Label(self.canvas, image=self.square_image)
        # self.square_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)
        #  add the square image to the canvas and make it appear on the result image

        self.square_image_canvas = self.canvas.create_image(0, 0, image=self.square_image, anchor=tk.NW)
        self.bind("<Left>", self.left_key)
        self.bind("<Right>", self.right_key)
        self.bind("<Up>", self.up_key)
        self.bind("<Down>", self.down_key)
        self.rot = 0
        # when pressing the key 1 the square image will rotate 90 degrees clockwise and when pressing 2 it will rotate 90 degrees counter clockwise (the square image is the image of the square that appears on the result image)
        self.bind("1", self.rotate_square_image_clockwise)
        # self.canvas.bind("<B1-Motion>", self.rotate_image)


        # self.canvas.create_image(0, 0, image=self.square_image, anchor=tk.NW)

   #  import math
    def rotate_image(self, event):
        # Calculate the angle of rotation based on the change in mouse position
        dx = event.x - self.x * 3 / 2
        dy = event.y - (self.y - 50) / 2
        angle = -math.atan2(dy, dx) * 180 / math.pi
        # Rotate the image and update it on the canvas
        eww = Image.fromarray(cv2.cvtColor(self.square_image_array, cv2.COLOR_BGR2RGB)).resize((self.sx, self.sy))
        self.square_image = ImageTk.PhotoImage(eww.rotate(angle))
        self.canvas.itemconfig(self.square_image_canvas, image=self.square_image)
        # self.canvas.image = self.square_image  # keep reference to avoid garbage collection

    def rotate_square_image_clockwise(self, event):
        # rotate the square image 45 degrees clockwise
        self.sx, self.sy = self.sy, self.sx
        self.square_image = ImageTk.PhotoImage(
            Image.fromarray(cv2.cvtColor(self.square_image_array, cv2.COLOR_BGR2RGB)).resize((self.sx, self.sy)))
        self.canvas.itemconfig(self.square_image_canvas, image=self.square_image)
    def left_key(self, event):
        # dont let the square image go out of the canvas\
        c1 = self.canvas.coords(self.square_image_canvas)
        if c1[0] > 0:
            self.canvas.move(self.square_image_canvas, -10, 0)

    def right_key(self, event):
        # dont let the square image go out of the canvas
        c1 = self.canvas.coords(self.square_image_canvas)
        if c1[0] + self.sx < self.x * 3:
            self.canvas.move(self.square_image_canvas, 10, 0)



    def up_key(self, event):
        # dont let the square image go out of the canvas
        c1 = self.canvas.coords(self.square_image_canvas)
        if c1[1] > 0:
            self.canvas.move(self.square_image_canvas, 0, -10)

    def down_key(self, event):
        # dont let the square image go out of the canvas
        # get the pixel coordinates of the square image
        c1 = self.canvas.coords(self.square_image_canvas)
        if c1[1] + 30 + 2 * self.sy < self.y:
            self.canvas.move(self.square_image_canvas, 0, 10)

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

    def add_original_image(self, image):
        """
        get the original image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 200
        :param image: the original image
        :return:
        """
        self.original_image = ImageTk.PhotoImage(
            Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).resize((self.x, self.y)))
        # self.original_label = tk.Label(self.canvas, image=self.original_image)
        # self.original_label.place(relx=0.30, rely=0.5, anchor=tk.CENTER)
        self.canvas.create_image(0, 0, image=self.original_image, anchor=tk.NW)

    def add_result_image(self, image):
        """
        get the result image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 420
        :param image: the result image
        :return:
        """
        self.result_image = ImageTk.PhotoImage(Image.fromarray(image).resize((self.x, self.y)))
        # self.result_label = tk.Label(self.canvas, image=self.result_image)
        # self.result_label.place(relx=0.7, rely=0.5, anchor=tk.CENTER)
        self.canvas.create_image(self.x, 0, image=self.result_image, anchor=tk.NW)

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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
    print("Hello world")
