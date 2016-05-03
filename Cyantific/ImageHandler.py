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
		self.original_image = None
		self.textHandler = TH.TextHandler()
		self.converted = True

	def init_image(self, imagePath):
		self.original_image = cv2.imread(imagePath, cv2.CV_LOAD_IMAGE_GRAYSCALE)
		self.current_image = self.original_image
		self.write_curr_image()
		self.converted = True

	def black_and_white(self, thresh=128):
		if not self.converted:
			bw_im = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
		else:
			bw_im = self.original_image
		self.current_image = bw_im = cv2.threshold(bw_im, thresh, 255, cv2.THRESH_BINARY)[1]

		return bw_im

	def set_image(self, imagePath):
		self.current_image = cv2.imread(imagePath, cv2.CV_LOAD_IMAGE_GRAYSCALE)
		self.write_curr_image()

	def OCR(self, lang='jpn'):
		path = path=str("%s/current.jpg" %self.IMAGE_WRITE_PATH)
		output = pytesseract.image_to_string(Image.open(path), lang=lang)
		parsed = self.textHandler.form_compounds(output)
		print "Parsed Compounds ", parsed
		lookup = self.textHandler.dict_search(parsed, entrytype=1)
		kanji = self.textHandler.kanji_search(parsed)

		return parsed, lookup, kanji

	def crop_image(self, row1, col1, row2, col2):
		self.current_image = self.original_image = cropped_image = self.current_image[row1:row2, col1:col2]
		self.write_curr_image()
		if not self.converted:
			return cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
		else:
			return cropped_image

	def rotate_image(self, degrees, save=False):
		rows, cols = self.current_image.shape[:2]
		M = cv2.getRotationMatrix2D((cols/2, rows/2), degrees, 1)
		if not self.converted:
			rotated_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
		else:
			rotated_image = self.current_image
		rotated_image = cv2.warpAffine(rotated_image, M, (cols,rows))
		if save:
			self.converted = True
			self.current_image = self.original_image = rotated_image
			self.write_curr_image()

		return rotated_image

	def skew_image(self, points, newPoints, dx, dy):
	
		p1 = np.float32(points)
		p2 = np.float32(newPoints)
		skewMat = cv2.getPerspectiveTransform(p1, p2)

		skewed = cv2.warpPerspective(self.current_image, skewMat, (dx,dy))
		self.current_image = self.original_image = skewed

		return skewed

	def write_curr_image(self):
		self.original_image = self.current_image
		path=str("%s/current.jpg" %self.IMAGE_WRITE_PATH)
		cv2.imwrite(path, self.current_image)

