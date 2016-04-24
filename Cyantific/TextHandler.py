# -*- coding: utf-8 -*-
import pytesseract
import sqlite3
from sqlite3 import OperationalError
import cjktools
from cjktools.resources import kanjidic
from cjktools.resources.radkdict import RadkDict

class TextHandler(object):

	def __init__(self):

		self.conn = sqlite3.connect(".resources/j_edict.db")
		self.cur = self.conn.cursor()

		self.kanji_dictionary = kanjidic.Kanjidic()
		self.radical_dictionary = RadkDict()


	"""
		Simple method to perform a Kanji Dictionary lookup of a specific kanji
		Returns the meaning, onyomi, kunyomi, and radicals
	"""
	def kanji_search(self, kanji):

		if len(kanji) == None:
			print "Nothin Found"
			return None

		entries = []
		for k in kanji:
			keys = list(k)
			for key in keys:
				entry = self.kanji_dictionary.get(key, None)
				if not entry:
					return None
				else:
					gloss = ', '.join(entry.gloss)
					on_read = ', '.join(entry.on_readings)
					kun_read = ', '.join(entry.kun_readings)
					radicals = ', '.join(self.radical_dictionary[key])
					entries.append((key, gloss, on_read, kun_read, radicals))
		return entries
		#key = kanji.decode("utf-8")
		"""key = None
		entry = self.kanji_dictionary.get(key, None)
		if not entry:
			return None
		else:
			gloss = ', '.join(entry.gloss)
			on_read = ', '.join(entry.on_readings)
			kun_read = ', '.join(entry.kun_readings)
			radicals = ', '.join(self.radical_dictionary[key])
			return gloss, on_read, kun_read, radicals"""

	"""
		Simple method to perform a SQL dictionary lookup for a word
		Type [0, 1, 2, 3] specifies the entry entrytype. 0 would be for an exact match,
		1 for prefix, 2 for suffix, 3 for any words containing the compound
	"""
	def dict_search(self, kanjiList, entrytype=0):

		definitions = []
		
		for word in kanjiList:

			compound = None
			word = u''.join(word)
			#Format the search string
			#My code is just awful, but sqlite3 was being very frustrating
			if entrytype == 0:
				#compound = str('%s' %word)
				compound = word
			elif entrytype == 1:
				#compound = str('%s%%' %word)
				compound = word + "%"
			elif entrytype == 2:
				compound = str('%%%s' %word)
			elif entrytype == 3:
				compound = str('%%%s%%' %word)

			self.cur.execute("SELECT * FROM edict WHERE kanji LIKE ?", (compound,))
			definitions.append(self.cur.fetchall()[:5])

		return definitions

	def form_compounds(self, text):
		chars = list(text.decode("utf-8"))
		compounds = []
		i = 0
		count = 0
		comp = []
		for char in chars:
			if char >= u'\u4e00' and char <= u'\u9faf':
				comp.append(char)
				count += 1
			else:
				if count != 0:
					compounds.append(comp)
				comp = []
				count = 0
		if len(comp) > 0: compounds.append(comp)
		vals = [u''.join(com) for com in compounds]
		return vals


def main():
	print "All in order"

if __name__ == '__main__':
	main()
