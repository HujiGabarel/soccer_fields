# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from Modules.Main.Main import get_viable_landing_in_radius
import cv2
import threading


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
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
        self.x = 800
        self.y = 600
        flag = False
        if flag:
            self.geometry(f"{self.x}x{self.y}")
        else:
            # this is the size of the images original and result
            self.x = 500
            self.y = 500
            self.state("zoomed")
        picture_x_y = 150
        self.background_image = ImageTk.PhotoImage(Image.open("logo.png").resize((picture_x_y, picture_x_y)))
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        # place the buttons on the window with a nice layout
        # add an entry for entering, E, N, and S, insert the entry values into the search function
        position = tk.CENTER
        self.E = tk.Label(self, text="E: ")
        self.E.pack()
        self.E_entry = tk.Entry(self)
        self.E_entry.pack()
        self.N = tk.Label(self, text="N: ")
        self.N.pack()
        self.N_entry = tk.Entry(self)
        self.N_entry.pack()
        self.Radius = tk.Label(self, text="Radius in km: ")
        self.Radius.pack()
        self.Radius_entry = tk.Entry(self)
        self.Radius_entry.pack()

        # inserting the entry values into the search function
        # self.search_button = tk.Button(self, text="חפש", command=self.do)
        self.search_button = tk.Button(self, text="חפש", command=threading.Thread(target=self.do).start)
        self.search_button.pack()
        labels = [self.E, self.N, self.Radius, self.E_entry, self.N_entry, self.Radius_entry, self.search_button]
        start_x = 50
        gap = 2.6
        start_y = 20
        entry_width = 40
        height = 10
        level = 1
        self.E.place(x=start_x, y=start_y, anchor=position)
        self.E.config(font=("Arial", 12, "bold"), foreground="black")
        self.E_entry.place(x=50 * gap + start_x, y=start_y, anchor=position)
        self.E_entry.config(width=entry_width)
        self.N.place(x=100 * gap + start_x, y=start_y, anchor=position)
        self.N.config(font=("Arial", 12, "bold"), foreground="black")
        self.N_entry.place(x=150 * gap + start_x, y=start_y, anchor=position)
        self.N_entry.config(width=entry_width)
        start_x = 70
        self.Radius.place(x=start_x, y=start_y + 50 * level, anchor=position)
        self.Radius.config(font=("Arial", 12, "bold"), foreground="black")
        self.Radius_entry.place(x=70 * gap + start_x, y=start_y + 50 * level, anchor=position)
        self.Radius_entry.config(width=entry_width)
        self.search_button.place(x=180 * gap + start_x, y=start_y + 50 * level, anchor=position)
        self.search_button.config(background="green", foreground="white", font=("Arial", 12, "bold"))
        # put the background image on the window, right side to the buttons
        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(x=1400, y=80, anchor=position)

        self.original_image = Image.open("logo.png")
        self.result_image = Image.open("logo.png")
        # make self.original_image and self.result_image an array of the image
        self.original_image_array = np.array(self.original_image)
        self.result_image_array = np.array(self.result_image)
        # add the original image and the result image to the window
        self.add_original_image(self.original_image_array)
        self.add_result_image(self.result_image_array)

    def do(self):
        # get the entry values
        self.E_value = self.E_entry.get()
        self.N_value = self.N_entry.get()
        self.Radius_value = self.Radius_entry.get()
        coordinates = (int(self.E_value), int(self.N_value), 36, "N")
        print(coordinates,self.Radius_value)
        # run the function
        image, total_mask = get_viable_landing_in_radius(coordinates, float(self.Radius_value))
        self.add_original_image(image)
        self.add_result_image(total_mask)

    def add_original_image(self, image):
        """
        get the original image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 200
        :param image: the original image
        :return:
        """
        self.original_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).resize((self.x, self.y)))
        self.original_label = tk.Label(self, image=self.original_image)
        self.original_label.place(x=self.x , y=self.y/ 1.5+100, anchor=tk.CENTER)

    def add_result_image(self, image):
        """
        get the result image in the form of array and put it on the window bellow the buttons, resize it to fit the x but the y should be 420
        :param image: the result image
        :return:
        """
        self.result_image = ImageTk.PhotoImage(Image.fromarray(image).resize((self.x, self.y)))
        self.result_label = tk.Label(self, image=self.result_image)
        self.result_label.place(x=self.x  * 2 + 20, y=self.y /1.5+100, anchor=tk.CENTER)

    def get_E_value(self):
        return self.E_value

    def get_N_value(self):
        return self.N_value

    def get_Radius_value(self):
        return self.Radius_value


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
