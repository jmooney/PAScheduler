
'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - EntryFieldArray
	
	Description:
		Maintains a grid of tkinter entry widgets. Handles automatic column resizing and scrollbar associations.
		
'''

# Imports
from tkinter import ttk
from tkinter import END
from tkinter import font

#-----------------------------------------------------#

class InputError(Exception):
	
	def __init__(self, *args):
		if not args:
			self.description = 'Invalid Input for an Entry'
		else:
			self.entry = args[0]
			self.text = args[1]
			self.description = 'Invalid Input "' + self.text + '" for Entry of Type ' + str(self.entry.getType())
		
		
		
#-----------------------------------------------------#

class TypedEntry(ttk.Entry):
	
	_invalidEntryStyle = None
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def __init__(self, parent, **kwArgs):
		super().__init__(parent, validate='focusout', validatecommand=self._validateOffFocus, **kwArgs)
		
		self._type = str
		self._isArray = False
		self._valRequired = False
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''	
	
	def getRaw(self):
		return super().get()
	def validate(self):
		self.get()
		
	def get(self):
		val = super().get()
		
		if val:
			try:
				val = [self._type(v) for v in val.split(self.getTypeArrayDivider())] if self._isArray else self._type(val)
				self['style'] = 'TEntry'
				return val
				
			except ValueError:
				self['style'] = self._invalidEntryStyle
				raise ValueError(self, val)
			
			
		elif self._valRequired:
			self['style'] = self._invalidEntryStyle
			raise ValueError(self, '')
		
		else:
			self['style'] = 'TEntry'
		
			
			
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''	
	
	def setInvalid(self):
		self['style'] = self._invalidEntryStyle
	def setValid(self):
		self['style'] = 'TEntry'
		
	def setType(self, type, req=False):
		self._isArray = isinstance(type, list)
		self._type = type if not self._isArray else type[0]
		self._valRequired = req
	
	def getTypeArrayDivider(self):
		try:
			return self._type.getArrayDivider()
		except AttributeError:
			return ' '
	
	def getType(self):
		return self._type
		
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''	
	
	def _validateOffFocus(self):
		valueRequired = self._valRequired
		self._valRequired = False

		success = True
		try:
			self.validate()
		except ValueError:
			success = False
			
		self._valRequired = valueRequired
		return success
	
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''	
	
	@classmethod
	def createStyle(cls):
		
		estyle = ttk.Style()

		estyle.element_create("plain.field", "from", "clam")
		estyle.layout("InvalidEntry.TEntry", [ ('Entry.plain.field', {'children': [ ('Entry.background', {'children': [(	\
							'Entry.padding', {'children': [( 'Entry.textarea', {'sticky': 'nswe'})], 'sticky': 'nswe'})], \
							'sticky': 'nswe'})], 'border':'2', 'sticky': 'nswe'})])
							
		estyle.configure("InvalidEntry.TEntry", background="white", foreground="black", fieldbackground='#F2B8B8')
		cls._invalidEntryStyle = "InvalidEntry.TEntry"
		
		
		
#------------------------------------------------------#

class EntryFieldArray(object):
	
	PixPerChar = 8.3
	PixPerRow = 27
	
	def __init__(self, parent, **kwArgs):
		self._parent = parent

		self.numRows = kwArgs['numRows']
		self.numCols = kwArgs['numCols']
		
		self._entries = []
		for i in range(self.numRows):
			row = []
			for j in range(self.numCols):
				entry = TypedEntry(parent)
				entry.grid(row=i, column=j)
				row.append(entry)
			self._entries.append(row)
		
		titledColumns = kwArgs.get('title')
		columnWidths = kwArgs.get('width')
		columnTypes = kwArgs.get('type')
		
		if titledColumns:
			self.setEntryTitles(titledColumns[0], **titledColumns[1])
		if columnWidths:
			self.setColumnWidths(columnWidths)
		if columnTypes:
			self.setColumnTypes(columnTypes)
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def setEntryTitles(self, titles, **kwArgs):
		entries = self.getRow(kwArgs['row']) if 'row' in kwArgs else (self.getColumn(kwArgs['col']) if 'col' in kwArgs else [])
		for entry in entries:
			entry.insert(0, titles[entries.index(entry)])
			entry.state(['readonly'])
		
	def setColumnWidths(self, widthTuples):
		for row in self._entries:
			for widthTuple in widthTuples:
				row[widthTuple[0]]['width'] = widthTuple[1]
				
	def setColumnTypes(self, columnTuples):
		for columnTuple in columnTuples:
			for entry in self.getColumn(columnTuple[0])[1:]:
				
				required = False
				if len(columnTuple) > 2:
					required = columnTuple[2]
					
				entry.setType(columnTuple[1], required)
				
				
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def validate(self):
		validInput = True
		
		for entryRow in self._entries:
			for entry in entryRow:
				try:
					entry.validate()
				except InputError:
					validInput = False
				
		if not validInput:
			raise InputError()


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def read(self):
		if self._isUnit:
			return self._entries.get()
		elif self._is1DArray:
			return [entry.get() for entry in self._entries]
		else:
			data = []	
			for row in self._entries:
				dataRow = []
				for entry in row:
					dataRow.append(entry.get())
				data.append(dataRow)				
			return data
			
			
	def readRaw(self):
		if self._isUnit:
			return self._entries.getRaw()
		elif self._is1DArray:
			return [entry.getRaw() for entry in self._entries]
		else:
			data = []	
			for row in self._entries:
				dataRow = []
				for entry in row:
					dataRow.append(entry.getRaw())
				data.append(dataRow)				
			return data
			
			
			
	def write(self, data):
		data = self._parseWriteData(data)
				
		if self._isUnit:
			self._entries.delete(0, END)
			self._entries.insert(0, str(data))
		
		elif self._is1DArray:
			for i in range(len(data)):
				self._entries[i].delete(0, END)
				self._entries[i].insert(0, str(data[i]))
		
		else:
			for i in range(len(data)):
				for j in range(len(data[i])):
					self._entries[i][j].delete(0, END)
					self._entries[i][j].insert(0, str(data[i][j]))
				
	
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getEntry(self, r, c):
		return EntryFieldSubArray(self.getSubArray(begin=(r, c), end=(r, c))._entries[0][0], isUnit=True)
	def getRow(self, r):
		return self.getRows([r])
	def getColumn(self, c):
		return self.getColumns([c])
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def getRows(self, rowIndices):
		rows = []
		for i in rowIndices:
			rows.append(self._entries[i])
		
		is1D = len(rows) == 1
		rows = rows[0] if is1D else rows
		return EntryFieldSubArray(rows, is1DArray=True)
		
		
	def getColumns(self, colIndices):
		cols = []
		for j in colIndices:
			cols.append([row[j] for row in self._entries])
			
		is1D = len(cols) == 1
		cols = cols[0] if is1D else cols
		
		return EntryFieldSubArray(cols, is1DArray=True)
		
		
	def getSubArray(self, begin, end):
		entries = []
		for entryRow in self._entries[begin[0]:end[0]+1]:
			row = []
			for entry in entryRow[begin[1]:end[1]+1]:
				row.append(entry)
			entries.append(row)
		return EntryFieldSubArray(entries)

		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def resizeToFit(self, data, **kwArgs):
		data = self._parseWriteData(data)
			
		row = kwArgs.get('row', 0)
		col = kwArgs.get('col', 0)
		begin = kwArgs.get('begin', (row, col))
		
		is1DList = isinstance(data,list)
		is2DList = is1DList and isinstance(data[0], list)
		
		endRow = begin[0] + (len(data) if is1DList else 0) -1;	numRows = endRow+1
		endCol  = begin[1] + (len(data[0]) if is2DList else 0) -1;	numCols = endCol+1

		if numRows > self.numRows:
			self.resize(numRows = numRows) 
		if numCols > self.numCols:
			self.resize(numCols = numCols)


	def resize(self, **kwArgs):
		rows = kwArgs.get('numRows', self.numRows)
		cols = kwArgs.get('numCols', self.numCols)
		
		extraRows = rows-self.numRows
		extraCols = cols-self.numCols
		
		#	Add or Remove Rows
		if extraRows < 0:
			for entry in self._entries[extraRows:]:
				entry.destroy()
			del(self._entries[extraRows:])
		else:
			for i in range(extraRows):
				row = []
				for j in range(self.numCols):
					entry = TypedEntry(self._parent)
					entry['width'] = self._entries[0][j]['width']
					entry.grid(row=i+self.numRows, column=j)
					row.append(entry)
				self._entries.append(row)
		self.numRows += extraRows
					
		#	Add or Remove Columns
		for i in range(len(self._entries)):
			row = self._entries[i]

			if extraCols < 0:
				for entry in row[extraCols:]:
					entry.destroy()
				del(row[extraCols:])
			else:
				columnWidths = kwArgs.get('widths')
				
				for j in range(extraCols):
					entry = TypedEntry(self._parent)
					entry.grid(row=i, column=j+self.numCols)
					row.append(entry)
				if columnWidths:
					self.setColumnWidths(columnWidths)
		
		self.numCols += extraCols

		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _parseWriteData(self, data):
		rows = data
		if isinstance(data, str):
			rows = [];	rowStrings = data.split('\n')
			for rowString in rowStrings:
				columns = rowString.split('\t')
				rows.append(columns)
			
			if len(rows) == 1:
				rows = rows[0]
			if len(rows) == 1:
				rows = rows[0]
		return rows	
				
				
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getWidth(self):
		return sum([entry['width'] for entry in self._entries[0]])*self.PixPerChar if self._entries else 0
	def getHeight(self):
		return self.numRows*self.PixPerRow

		
#------------------------------------------------------#

class EntryFieldSubArray(EntryFieldArray):
	
	def __init__(self, entries, **kwArgs):
		self._entries = entries
		self._isUnit = kwArgs.get('isUnit', False)
		self._is1DArray = kwArgs.get('is1DArray', False)
		
		if self._isUnit:
			self.numEntries = 1
		elif self._is1DArray:
			self.numEntries = len(self._entries)
		else:
			self.numRows = len(self._entries)
			self.numCols = len(self._entries[0]) if self._entries else 0
		
		
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def get(self):
		return self._entries
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def resize(self):
		raise AttributeError("'EntryFieldSubArray' has no attribute 'resize'")
	def resizeToFit(self):
		raise AttributeError("'EntryFieldSubArray' has no attribute 'resizeToFit'")
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def __iter__(self):
		return self._entries.__iter__()
	def next(self):
		return self._entries.next()
	def __len__(self):
		return self._entries.__len__()
	def __getitem__(self, i):
		return self._entries.__getitem__(i)
	def index(self, i):
		return self._entries.index(i)
		