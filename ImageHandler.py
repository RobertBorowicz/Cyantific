# -*- coding: utf-8 -*-
import Image, ImageTk
import cv2
import numpy as np
import TextHandler as TH
import pytesseract

class ImageHandler(object):

	def __init__(self):

		self.IMAGE_WRITE_PATH = ".resources"
		self.current_image = None
		self.textHandler = TH.TextHandler()

	def black_and_white(self, thresh=128):
		self.current_image = bw_im = cv2.threshold(self.current_image, thresh, 255, cv2.THRESH_BINARY)[1]
		path = str("%s/bw.jpg" %self.IMAGE_WRITE_PATH)
		cv2.imwrite(path, bw_im)
		self.write_curr_image()
		return path

	def set_image(self, imagePath):
		self.current_image = cv2.imread(imagePath)#, cv2.CV_LOAD_IMAGE_GRAYSCALE)
		self.write_curr_image()

	def OCR(self, lang='jpn'):
		path = path=str("%s/current.jpg" %self.IMAGE_WRITE_PATH)
		output = pytesseract.image_to_string(Image.open(path), lang=lang)
		parsed = self.textHandler.form_compounds(output)
		print output, '\n', parsed

	def crop_image(self, row1, col1, row2, col2):
		self.current_image = cropped_image = self.current_image[row1:row2, col1:col2]
		path = str("%s/cropped.jpg" %self.IMAGE_WRITE_PATH)
		cv2.imwrite(path, cropped_image)
		self.write_curr_image()
		return path

	def write_curr_image(self):
		path=str("%s/current.jpg" %self.IMAGE_WRITE_PATH)
		cv2.imwrite(path, self.current_image)
