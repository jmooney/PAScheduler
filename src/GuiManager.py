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
		
		self._fileManager = fileManager
		self._createMenus(fileManager)
		
		tf = self._topFrame = ttk.Frame(self._window)
		tf.grid(column=0, row=0, sticky=(N, W, E, S))
		tf.columnconfigure(0, weight=1)
		tf.rowconfigure(0, weight=1)
		
		self._createNotebook()
		self._registerEvents()
		
		return win
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _createMenus(self, fileManager):
		self._nameCheckMenu = IntVar()
		self._majorCheckMenu = IntVar()
		self._emailCheckMenu = IntVar()
		self._yearCheckMenu = IntVar()
		self._viewNameRadio = StringVar()
		
		self._menubar = Menu(self._window)
		self._menuFile = Menu(self._menubar)
		self._menuSchedule = Menu(self._menubar)
		self._menuHelp = Menu(self._menubar)
		self._menuPopup = Menu(self._window, tearoff=0)
		
		self._menubar.add_cascade(menu = self._menuFile, label = "File")
		self._menubar.add_cascade(menu = self._menuSchedule, label = "Schedule")
		self._menubar.add_cascade(menu = self._menuHelp, label = "Help")
		
		self._menuFile.add_command(label="New Project", command=fileManager.newFile)
		self._menuFile.add_command(label="Open Project...", command=fileManager.openFile)
		self._menuFile.add_separator()
		self._menuFile.add_command(label="Save Project", command=fileManager.saveFile)
		self._menuFile.add_command(label="Save Project As...", command=fileManager.saveFileAs)
		self._menuFile.add_command(label="Save Schedule As...")
		self._menuFile.add_separator()
		self._menuFile.add_command(label='Quit', command=fileManager.askQuit)
		
		self._menuSchedule.add_command(label="Create", command=self._schedule.createSchedule)
		self._menuSchedule.add_separator()
		self._menuSchedule.add_command(label="Sort By Last Name", command=partial(self._schedule.sortAdvisors, lambda advisor:advisor.name.partition(' ')[2]))
		self._menuSchedule.add_command(label="Sort By Major", command=partial(self._schedule.sortAdvisors, lambda advisor:advisor.major))
		self._menuSchedule.add_separator()
		self._menuSchedule.add_checkbutton(label="View Name", variable=self._nameCheckMenu, onvalue=1, offvalue=0, command=self._schedule.updateText)
		self._menuSchedule.add_checkbutton(label="View Major", variable=self._majorCheckMenu, onvalue=1, offvalue=0, command=self._schedule.updateText)
		self._menuSchedule.add_checkbutton(label="View Email", variable=self._emailCheckMenu, onvalue=1, offvalue=0, command=self._schedule.updateText)
		self._menuSchedule.add_checkbutton(label="View Year", variable=self._yearCheckMenu, onvalue=1, offvalue=0, command=self._schedule.updateText)
		self._menuSchedule.add_separator()
		self._menuSchedule.add_radiobutton(label="First Name", variable=self._viewNameRadio, value="first", command=self._schedule.updateText)
		self._menuSchedule.add_radiobutton(label="Last Name", variable=self._viewNameRadio, value="last", command=self._schedule.updateText)
		self._viewNameRadio.set("first")
		self._nameCheckMenu.set(1)
		
		self._menuHelp.add_command(label="About")
		self._menuHelp.add_command(label="Frequently Asked Questions")
		
		self._menuPopup.add_command(label="Select", command=partial(self._onPageClick, "select"))
		self._menuPopup.add_command(label="Save As...", command=partial(self._onPageClick, "saveAs"))
		self._menuPopup.add_separator()
		self._menuPopup.add_command(label="Close", command=partial(self._onPageClick, "close"))
		
		self._window['menu'] = self._menubar
	
	
	def _createNotebook(self):
		nb = self._notebook = ttk.Notebook(self._topFrame, name="mainNotebook", padding=(8, 20, 0, 0))
		nb.grid(row=0, column=0, sticky=(N, W, E, S))
		nb.bind('<<NotebookTabChanged>>', self._associateNBScrollbar)
		
		self._hzScrollBar = ttk.Scrollbar(self._topFrame, orient=HORIZONTAL);	self._hzScrollBar.grid(row=1, column=0, sticky=(N,W,E,S))
		self._vScrollBar = ttk.Scrollbar(self._topFrame, orient=VERTICAL);		self._vScrollBar.grid(row=0, column=1, sticky=(N,W,E,S))
		
		self.createPage('Mentor Information', EntryPage, {'numRows':31, 'numCols':8, 'title':[['Name', 'Email', 'Major', 'Year', 'Minimum Hours', 'Requested Hours', 'Maximum Hours', 'Availability'],\
								{'row':0}], 'width':[(0, 25), (1, 25), (7, 70)], 'type':[(1, str, True), (2, str, True), (3, int, True), (4, float), (5, float), (6, float), (7, [Time], True)]})
																
		self.createPage('Schedule Settings', EntryPage, {'numRows':9, 'numCols':2, 'title':[['Description', 'Value'], {'row':0}], 'width':[(0,70)]})
		self._createSettings()
	
	
	def _registerEvents(self):
		self._window.bind("<Button-3>", self._OnMouse3)
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getViewOptions(self):
		keys = ['name', 'major', 'email', 'year']
		
		values = ['']
		if self._nameCheckMenu.get() == 1:
			values = [self._viewNameRadio.get()]
			
		boolSVars = [self._majorCheckMenu, self._emailCheckMenu, self._yearCheckMenu]
		for sVar in boolSVars:
			val = sVar.get()
			values.append(bool(val) if val else False)
			
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
	def getPageName(self, tabIndex):
		return self._notebook.tab(tabIndex, 'text')
	def getPages(self):
		return self._pages
	def getNotebook(self):
		return self._notebook
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _associateNBScrollbar(self, *args):
		pageName = self._notebook.tab(self._notebook.select(), 'text')
		canvas = self._pages[pageName].getCanvas()
		
		self._hzScrollBar['command'] = canvas.xview; canvas['xscrollcommand'] = self._hzScrollBar.set
		self._vScrollBar['command'] = canvas.yview;	canvas['yscrollcommand'] = self._vScrollBar.set
		
		
	def _OnMouse3(self, event):
		widgetName = str(event.widget)
		if not (widgetName.endswith("mainNotebook")):
			return

		#	Identify Selected Page
		self._clickedNotebookTab = 0
		try:
			self._clickedNotebookTab = event.widget.index("@{x},{y}".format(x=event.x, y=event.y))
		except TclError:
			return
		
		# Enable/Disable Popup Options and Display
		if(self._clickedNotebookTab <= 1):
			self._menuPopup.entryconfig(4, state=DISABLED)
		else:
			self._menuPopup.entryconfig(4, state=NORMAL)
		self._menuPopup.post(event.x + self._window.winfo_x(), event.y+self._window.winfo_y())
		
		
	def _onPageClick(self, menuOption):
		if(menuOption == "select"):
			self._notebook.select(self._clickedNotebookTab)
		elif(menuOption == "saveAs"):
			self._fileManager.savePageAs(self._clickedNotebookTab)
		elif(menuOption == "close"):
			del(self._pages[self.getPageName(self._clickedNotebookTab)])
			self._notebook.forget(self._clickedNotebookTab)
		

	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def _createSettings(self):
		settingsPage = self._pages['Schedule Settings']
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
		
	def reset(self):
		self._notebook.destroy()
		self._createNotebook()

