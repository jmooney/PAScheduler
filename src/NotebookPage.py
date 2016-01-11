'''

	Author:	John Mooney
	Date:		08/08/2013
	
	PAScheduler 2 - NotebookPage
	
	Description:
		The variuos pages that may be added to a notebook item
		
'''

# Imports
from tkinter import *
from tkinter import ttk
from .EntryFieldArray import EntryFieldArray


#------------------------------------------------------------------#

class NotebookPage(object):

	def __init__(self, notebook, tid, name, data={}):
		super().__init__()
		
		self._id = tid
		self._name = name
		self._owner = notebook
		
		self._canvas = Canvas(notebook)
		self._canvas.pack(side=LEFT, expand=True, fill=BOTH)
		
		self._frame = ttk.Frame(self._canvas)
		self._frame.columnconfigure(0, weight=1)
		self._frame.rowconfigure(0, weight=1)
		
		self._createGUI(data)
		
		self._canvas.create_window(0, 0, window=self._frame, anchor=NW)
		self._canvas['scrollregion']=(0, 0, self.getWidth(), self.getHeight())
		
		notebook.add(self._canvas, text=name)

		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def _createGUI(self, data):
		raise NotImplementedError

	def getCanvas(self):
		return self._canvas
		
	def getWidth(self):
		raise NotImplementedError	
	def getHeight(self):
		raise NotImplementedError


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getName(self):	
		return self._name
	def setName(self, name):
		self._owner.tab(self._id, text=name)
		self._name = name


#----------------------------------------------------------------#

class EntryPage(NotebookPage):
	
	def _createGUI(self, data):
		self._entryFieldArray = EntryFieldArray(self._frame, **data)
	

	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getEntryArray(self):
		return self._entryFieldArray
	
	def getEntries(self, **kwArgs):
		'''	'pos' -> One Entry
			'row' -> List of Entries
			'col' -> List of Entries
			'rows' -> List of List of Entries
			'cols' -> List of List of Entries
			'begin' -> Beginning Index of Entry Sub Array
			'end' -> Ending Index of Sub Array
		'''	
		
		ef = self._entryFieldArray
		
		if kwArgs.get('pos'):
			return ef.getEntry(kwArgs['pos'][0], kwArgs['pos'][1])
		elif kwArgs.get('row') != None:
			return ef.getRow(kwArgs['row'])
		elif kwArgs.get('col') != None:
			return ef.getColumn(kwArgs['col'])
		elif kwArgs.get('rows'):
			return ef.getRows(kwArgs['rows'])
		elif kwArgs.get('cols'):
			return ef.getColumns(kwArgs['cols'])
		else:
			return ef.getSubArray(kwArgs.get('begin', (0, 0)), kwArgs.get('end', (ef.numRows-1, ef.numCols-1)))


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def read(self, **kwArgs):
		return self.getEntries(**kwArgs).read()
	def readRaw(self, **kwArgs):
		return self.getEntries(**kwArgs).readRaw()
	
	def write(self, data, **kwArgs):
		self._entryFieldArray.resizeToFit(data, **kwArgs)
		self.getEntries(**kwArgs).write(data)
		self._canvas['scrollregion'] = (0, 0, self._entryFieldArray.getWidth(), self._entryFieldArray.getHeight())
	
	def validate(self):
		return self.getEntries().validate()
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getWidth(self):
		return self._entryFieldArray.getWidth()
	def getHeight(self):
		return self._entryFieldArray.getHeight()

