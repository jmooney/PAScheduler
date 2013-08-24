'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - GuiManager
	
	Description:
		Maintains and creates the windowed GUI.
		
'''

# Imports
from tkinter import *
from tkinter import ttk
from TimeObj import Time, DayDensity
from NotebookPage import *


#------------------------------------------------------------------#

class GuiManager(object):

	PixPerChar = 8.3;		PixPerRow = 27;

	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def __init__(self, schedule):
		super().__init__()
		
		self._schedule = schedule
		self._pages = {}	
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def createWindow(self, fileManager):
		win = self._window = Tk()
		win.title("Peer Adviser Scheduling")
		win.geometry("800x600")
		win.rowconfigure(0, weight=1)
		win.columnconfigure(0, weight=1)
		win.option_add('*tearOff', FALSE)
		win.minsize(400, 300)
		
		self._createMenu(fileManager)

		tf = self._topFrame = ttk.Frame(self._window)
		tf.grid(column=0, row=0, sticky=(N, W, E, S))
		tf.columnconfigure(0, weight=1)
		tf.rowconfigure(0, weight=1)
		
		self._createNotebook()
		
		return win
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _createMenu(self, fileManager):
		self._menubar = Menu(self._window)
		self._menuFile = Menu(self._menubar)
		self._menuSchedule = Menu(self._menubar)
		self._menubar.add_cascade(menu = self._menuFile, label = "File")
		self._menubar.add_cascade(menu = self._menuSchedule, label = "Schedule")
		
		self._menuFile.add_command(label="New", command=fileManager.newFile)
		self._menuFile.add_command(label="Open...", command=fileManager.openFile)
		self._menuFile.add_command(label="Save", command=fileManager.saveFile)
		self._menuFile.add_command(label="Save As...", command=fileManager.saveFileAs)
		self._menuFile.add_command(label="Export to Excel...")
		self._menuFile.add_command(label="Export to PDF...")
		self._menuFile.add_command(label='Quit', command=quit)
		self._menuSchedule.add_command(label="Create", command=self._schedule.createSchedule)
		self._window['menu'] = self._menubar
	
	
	def _createNotebook(self):
		nb = self._notebook = ttk.Notebook(self._topFrame, padding=(8, 20, 0, 0))
		nb.grid(row=0, column=0, sticky=(N, W, E, S))
		nb.bind('<<NotebookTabChanged>>', self._associateNBScrollbar)
		
		self._hzScrollBar = ttk.Scrollbar(self._topFrame, orient=HORIZONTAL);	self._hzScrollBar.grid(row=1, column=0, sticky=(N,W,E,S))
		self._vScrollBar = ttk.Scrollbar(self._topFrame, orient=VERTICAL);		self._vScrollBar.grid(row=0, column=1, sticky=(N,W,E,S))
		
		self.createPage('Advisers', EntryPage, (1, 0), {'numRows':30, 'numCols':7, 'title':[['Name', 'Major', 'Year', 'Min. Hrs', 'Req. Hrs', 'Max Hrs.', 'Availability'], {'row':0}], 'width':[(0, 25), (6, 70)], \
																'type':[(1, str, True), (2, int, True), (3, float), (4, float), (5, float), (6, [Time], True)]})
																
		self.createPage('Settings', EntryPage, (1, 0), {'numRows':10, 'numCols':2, 'title':[['Description', 'Value'], {'row':0}], 'width':[(0,70)]})
		self._createSettings()
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def createPage(self, name, pageType, pageDataBegin, pageData):
		self._pages[name] = pageType(self._notebook, name, pageDataBegin, pageData)
		return self._pages[name]
		
	def getPage(self, name):
		return self._pages[name]
	def getPages(self):
		return self._pages
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _associateNBScrollbar(self, *args):
		pageName = self._notebook.tab(self._notebook.select(), 'text')
		canvas = self._pages[pageName].getCanvas()
		
		self._hzScrollBar['command'] = canvas.xview;	canvas['xscrollcommand'] = self._hzScrollBar.set
		self._vScrollBar['command'] = canvas.yview;	canvas['yscrollcommand'] = self._vScrollBar.set
		
		
	def _createSettings(self):
		settingsPage = self._pages['Settings']
		settingsPage.write('Advising Hours\tM-Th 9-5; F 10-12\n' + \
									'Number of Active Advisers\tM-Th 3; F 2\n' + \
									'Time Slot Duration (minutes)\t15\n' + \
									'Minimum Consecutive Hours\t1\n' + \
									'Maximum Consecutive Hours\t3\n' + \
									'Minimum Consecutibe Break Hours\t1.5\n' + \
									'Maximum Hours per Week\t7', begin=(1,0))
		
		entryTypes = [[Time], [DayDensity], int, float, float, float, float]

		descEntries = settingsPage.getEntries(col=0)
		valueEntries = settingsPage.getEntries(col=1)[1:]

		for entry in descEntries:
			entry.state(['readonly'])
		for i in range(len(entryTypes)):
			valueEntries[i].setType(entryTypes[i], True)
			
			
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def reset(self):
		self._notebook.destroy()
		self._createNotebook()

