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
from .NotebookPage import *
from functools import partial
from .TimeObj import Time, DayDensity
from .EntryFieldArray import InputError


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
		win.title("VSE Peer Mentor Scheduling Program v2.30")
		win.geometry("800x600")
		win.rowconfigure(0, weight=1)
		win.columnconfigure(0, weight=1)
		win.option_add('*tearOff', FALSE)
		win.minsize(400, 300)
		win.protocol("WM_DELETE_WINDOW", fileManager.askQuit)
		
		self._createMenu(fileManager)

		tf = self._topFrame = ttk.Frame(self._window)
		tf.grid(column=0, row=0, sticky=(N, W, E, S))
		tf.columnconfigure(0, weight=1)
		tf.rowconfigure(0, weight=1)
		
		self._createNotebook()
		
		return win
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _createMenu(self, fileManager):
		self._firstCheckMenu = StringVar()
		self._lastCheckMenu = StringVar()
		self._majorCheckMenu = StringVar()
		self._emailCheckMenu = StringVar()
		self._yearCheckMenu = StringVar()
		
		self._menubar = Menu(self._window)
		self._menuFile = Menu(self._menubar)
		self._menuSchedule = Menu(self._menubar)
		self._menubar.add_cascade(menu = self._menuFile, label = "File")
		self._menubar.add_cascade(menu = self._menuSchedule, label = "Schedule")
		
		self._menuFile.add_command(label="New", command=fileManager.newFile)
		self._menuFile.add_command(label="Open...", command=fileManager.openFile)
		self._menuFile.add_command(label="Save", command=fileManager.saveFile)
		self._menuFile.add_command(label="Save As...", command=fileManager.saveFileAs)
		self._menuFile.add_command(label="Save Page As...", command=fileManager.savePageAs)
		self._menuFile.add_separator()
		self._menuFile.add_command(label='Quit', command=fileManager.askQuit)
		self._menuSchedule.add_command(label="Create", command=self._schedule.createSchedule)
		self._menuSchedule.add_command(label="Validate", command=self._validateInput)
		self._menuSchedule.add_separator()
		self._menuSchedule.add_command(label="Sort By Last Name", command=partial(self._schedule.sortAdvisors, lambda advisor:advisor.name.partition(' ')[2]))
		self._menuSchedule.add_command(label="Sort By Major", command=partial(self._schedule.sortAdvisors, lambda advisor:advisor.major))
		self._menuSchedule.add_separator()
		self._menuSchedule.add_checkbutton(label="View First Name", variable=self._firstCheckMenu, onvalue='first', offvalue='', command=self._schedule.updateText)
		self._menuSchedule.add_checkbutton(label="View Last Name", variable=self._lastCheckMenu, onvalue='last', offvalue='', command=self._schedule.updateText)
		self._menuSchedule.add_checkbutton(label="View Major", variable=self._majorCheckMenu, onvalue=1, offvalue=0, command=self._schedule.updateText)
		self._menuSchedule.add_checkbutton(label="View Email", variable=self._emailCheckMenu, onvalue=1, offvalue=0, command=self._schedule.updateText)
		self._menuSchedule.add_checkbutton(label="View Year", variable=self._yearCheckMenu, onvalue=1, offvalue=0, command=self._schedule.updateText)
		self._window['menu'] = self._menubar
	
	
	def _createNotebook(self):
		nb = self._notebook = ttk.Notebook(self._topFrame, padding=(8, 20, 0, 0))
		nb.grid(row=0, column=0, sticky=(N, W, E, S))
		nb.bind('<<NotebookTabChanged>>', self._associateNBScrollbar)
		
		self._hzScrollBar = ttk.Scrollbar(self._topFrame, orient=HORIZONTAL);	self._hzScrollBar.grid(row=1, column=0, sticky=(N,W,E,S))
		self._vScrollBar = ttk.Scrollbar(self._topFrame, orient=VERTICAL);		self._vScrollBar.grid(row=0, column=1, sticky=(N,W,E,S))
		
		self.createPage('Advisors', EntryPage, {'numRows':31, 'numCols':8, 'title':[['Name', 'Email', 'Major', 'Year', 'Minimum Hours', 'Requested Hours', 'Maximum Hours', 'Availability'],\
								{'row':0}], 'width':[(0, 25), (1, 25), (7, 70)], 'type':[(1, str, True), (2, str, True), (3, int, True), (4, float), (5, float), (6, float), (7, [Time], True)]})
																
		self.createPage('Settings', EntryPage, {'numRows':9, 'numCols':2, 'title':[['Description', 'Value'], {'row':0}], 'width':[(0,70)]})
		self._createSettings()
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getViewOptions(self):
		keys = ['name', 'major', 'email', 'year']
		
		if self._firstCheckMenu.get():
			values = ['first']
		elif self._lastCheckMenu.get():
			values = ['last']
		else:
			values = ['']
		
		boolSVars = [self._majorCheckMenu, self._emailCheckMenu, self._yearCheckMenu]
		for sVar in boolSVars:
			val = sVar.get()
			values.append(bool(int(val)) if val else False)
			
		ops = {}
		for i in range(len(keys)):
			ops[keys[i]] = values[i]
		return ops
			
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def createPage(self, name, pageType, pageData):
		self._pages[name] = pageType(self._notebook, name, pageData)
		return self._pages[name]
		
	def getPage(self, name):
		return self._pages[name]
	def getPages(self):
		return self._pages
	def getNotebook(self):
		return self._notebook
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _associateNBScrollbar(self, *args):
		pageName = self._notebook.tab(self._notebook.select(), 'text')
		canvas = self._pages[pageName].getCanvas()
		
		self._hzScrollBar['command'] = canvas.xview;	canvas['xscrollcommand'] = self._hzScrollBar.set
		self._vScrollBar['command'] = canvas.yview;	canvas['yscrollcommand'] = self._vScrollBar.set
		
		
	def _createSettings(self):
		settingsPage = self._pages['Settings']
		settingsPage.write('Advising Hours\tM-Th 10-6; F 10-1\n' + \
									'Number of Active Advisors\tM-Th 3; F 2\n' + \
									'Time Slot Duration (minutes)\t15\n' + \
									'Minimum Consecutive Hours\t1\n' + \
									'Maximum Consecutive Hours\t3\n' + \
									'Minimum Consecutive Break Hours\t1.5\n' + \
									'Minimum Hours per Week\t3\n' + \
									'Maximum Hours per Week\t7', begin=(1,0))
		
		entryTypes = [[Time], [DayDensity], int, float, float, float, float, float]

		descEntries = settingsPage.getEntries(col=0)
		valueEntries = settingsPage.getEntries(col=1)[1:]

		for entry in descEntries:
			entry.state(['readonly'])
		for i in range(len(entryTypes)):
			valueEntries[i].setType(entryTypes[i], True)
			
			
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _validateInput(self):
		try:
			current = self._notebook.select()
			
			self._schedule.getValidAdvisorEntries()
			self._notebook.select(self._notebook.tabs()[1])
			self._pages['Settings'].validate()
			self._notebook.select(current)
		except ValueError:
			pass
				
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def reset(self):
		self._notebook.destroy()
		self._createNotebook()

