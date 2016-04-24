# -*- coding: utf-8 -*-
import Tkinter as tk
from tkFileDialog import askopenfilename
import Image, ImageTk
import cv2
from ttk import Frame, Button, Label, Style, Entry
import ImageHandler as IH
from random import randint


class Cyantific(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.master.title("Cyantific")

        #self.GUIFrame = Frame(self)
        #Load image related elements
        #self.loadFrame = Frame(self)
        self.loadButton = Button(self)

        #Cropping related GUI elements
        #self.cropFrame = Frame(self)
        self.cropButton = Button(self)
        self.OCRButton = Button(self)
        self.BWSlider = tk.Scale(self)
        self.BWButton = Button(self)
        self.XScroll = tk.Scrollbar(self)
        self.YScroll = tk.Scrollbar(self)

        self.canvas = None
        self.cropRect = None
        self.startX = self.startY = None
        self.currX = self.currY = None
        self.cropping = False

        self.imageHandler = IH.ImageHandler()

        self.initUI()
        self.filename = None
        self.image_dims = None

        self.converting_bw = False

    def initUI(self):
        self.pack(fill=tk.BOTH, expand=True)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)

        label = Label(self, text="Image")
        label.grid(sticky=tk.W+tk.S, pady=4, padx=5)

        self.canvas = tk.Canvas(self)
        self.canvas.config(cursor="cross", xscrollcommand=self.XScroll.set, yscrollcommand=self.YScroll.set)
        self.canvas.grid(row=1, column=1, columnspan=2, rowspan=4, sticky=tk.N+tk.S+tk.E+tk.W)
        #self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.XScroll.config(orient=tk.HORIZONTAL, command=self.canvas.xview, width=20)
        self.YScroll.config(orient=tk.VERTICAL, command=self.canvas.yview, width=20)
        self.XScroll.grid(row=0, column=1, columnspan=2)
        self.YScroll.grid(row=2, column=0, rowspan=4)

        #self.GUIFrame.grid(row=0, column=1)

        #Loading elements
        #self.loadFrame.grid(row=1, column=1)
        self.loadButton.config(text="Load Image", command=self.load_image)
        self.loadButton.grid(row=1, column=4)
        
        #Cropping elements
        #self.cropFrame.grid(row=0, column=1)
        self.cropButton.config(text="Start Cropping", command=self.set_cropping, state=tk.DISABLED)
        self.cropButton.grid(row=5, column=4, pady=4)

        self.OCRButton.config(text="OCR Image", command=self.OCR_image, state=tk.DISABLED)
        self.OCRButton.grid(row=5, column=5, padx=5)

        self.BWSlider.config(from_=0, to=255, orient=tk.HORIZONTAL, label="B&W Threshold", command=self.slider_update_bw, state=tk.DISABLED)
        self.BWSlider.set(128)
        self.BWSlider.grid(row=4, column=4)
        self.BWButton.config(text="Convert to B&W", command=self.toggle_bw, state=tk.DISABLED)
        self.BWButton.grid(row=4, column=5)


    def slider_update_bw(self, event):
        thresh = self.BWSlider.get()
        if (self.converting_bw):
            self.black_and_white(thresh)

    def draw_image(self, path=None):
        fpath = None
        if path == None:
            fpath = self.filename
        else:
            fpath = path

        self.imageHandler.init_image(fpath)

        self.im = Image.open(fpath)
        dimX, dimY = self.im.size
        self.canvas.config(scrollregion=(0, 0, dimX, dimY))
        self.image_dims = (dimY, dimX)
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.canvas.create_image(0,0,anchor="nw",image=self.tk_im)
        self.canvas.config(width=dimX, height=dimY)

    def draw_from_array(self, image):
        self.im = Image.fromarray(image)
        dimX, dimY = self.im.size
        print dimX, dimY
        self.image_dims = (dimY, dimX)
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.canvas.create_image(0,0,anchor="nw",image=self.tk_im)
        self.canvas.config(width=dimX, height=dimY)

    def on_button_press(self, event):
        if self.cropping:
            print self.XScroll.get()
            self.startX = event.x
            self.startY = event.y

            if not self.cropRect:
            	self.cropRect = self.canvas.create_rectangle(0, 0, 1, 1, fill="", outline="lightgreen", width=5)

    def on_move_press(self, event):
        if self.cropping:
            self.currX, self.currY = (event.x, event.y)
            self.canvas.coords(self.cropRect, self.startX, self.startY, self.currX, self.currY)

    def load_image(self):
        self.canvas.delete(tk.ALL)
        self.cropRect = None
        self.filename = None
        self.filename = askopenfilename(filetypes=([("Image files", ("*.png","*.jpg","*.jpeg","*.gif","*.tiff"))]))
        if self.filename:
            self.draw_image(self.filename)
            self.cropButton.config(state=tk.NORMAL)
            self.OCRButton.config(state=tk.NORMAL)
            self.BWButton.config(state=tk.NORMAL)


    def on_button_release(self, event):
        pass

    def set_cropping(self):
        if not self.cropping:
            self.cropping = True
            self.cropButton.config(text="Save Crop")
        else:
            self.cropTop = tk.Toplevel(width=200, height=100)
            self.cropTop.title("Confirm crop")
            self.cropTop.resizable(width=None, height=None)
            label = Label(self.cropTop, text="Crop the image?", pad=5)
            label.pack()
            confirm = Button(self.cropTop, text="Confirm", pad=5, command=self.crop_image)
            confirm.pack(pady=5, padx=5)
            cancel = Button(self.cropTop, text="Cancel", pad=5, command=self.cancel_crop_top)
            cancel.pack(pady=5, padx=5)

    def cancel_crop_top(self):
        self.cropTop.destroy()
        self.cropButton.config(text="Save Crop")
        self.cropping = True

    def crop_image(self):
        self.cropTop.destroy()
        self.cropButton.config(text="Start Cropping")
        self.cropping = False
        c1, r1, c2, r2 = self.startX, self.startY, self.currX, self.currY
        if c1 > c2:
            c1 = self.currX
            c2 = self.startX
        if r1 > r2:
            r1 = self.currY
            r2 = self.startY
        
        cols = self.image_dims[1]
        rows = self.image_dims[0]
        c1 = 0 if (c1 < 0) else c1
        r1 = 0 if (r1 < 0) else r1
        c2 = cols-1 if (c2 >= cols) else c2
        r2 = rows-1 if (r2 >= rows) else r2

        image = self.imageHandler.crop_image(r1, c1, r2, c2)
        self.cropRect = None
        self.draw_from_array(image)

    def toggle_bw(self):
        if not self.converting_bw:
            self.BWSlider.config(state=tk.NORMAL)
            self.BWButton.config(text="Save Change")
            self.cropButton.config(state=tk.DISABLED)
            self.OCRButton.config(state=tk.DISABLED)
        else:
            self.BWSlider.config(state=tk.DISABLED)
            self.BWButton.config(text="Convert to B&W")
            self.cropButton.config(state=tk.NORMAL)
            self.OCRButton.config(state=tk.NORMAL)
            self.imageHandler.converted = True
            self.imageHandler.write_curr_image()
        self.converting_bw = (not self.converting_bw)

    def black_and_white(self, thresh=128):
        image = self.imageHandler.black_and_white(thresh)
        self.draw_from_array(image)

    def OCR_image(self):
        self.imageHandler.OCR()


def main():
	root = tk.Tk()
	app = Cyantific(root)
	root.mainloop()

if __name__ == '__main__':
	main()