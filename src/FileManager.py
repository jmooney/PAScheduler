
'''

	Author:	John Mooney
	Date:		08/23/2013
	
	PAScheduler 2 - FileManager
	
	Description:
		Manages opening and closing files for the PAScheduler
		
'''

# Imports
from tkinter import filedialog
from tkinter import messagebox
from .NotebookPage import *


#-----------------------------------------------------#

class FileManager(object):

	def __init__(self, guiMngr, schedule):
		self._guiMngr 		= guiMngr
		self._schedule 		= schedule
		self._isAltered 		= True
		self._workingFile 	= ""
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def newFile(self):
		if self._isAltered:
			message = self._askSaveDialog()
			if (message and not self.saveFile()) or message == None:
				return
		
		self._guiMngr.reset()
		self._schedule.reset()
		self._workingFile = ""
		
		
		
	def openFile(self):
		if self._isAltered:
			message = self._askSaveDialog()
			if (message and not self.saveFile()) or message == None:
				return
		
		filename = filedialog.askopenfilename(defaultextension='.pas', filetypes=[('PA Schedule Project', '.pas'), ('All types', '.*')])
		if not filename:
			return
		
		self._guiMngr.reset()
		self._schedule.reset()
			
		self._workingFile = filename
		with open(filename, 'r') as file:
			data = [line.rstrip() for line in file.readlines() if line.rstrip()]
		
		currentPage = None
		currentPageLines = []
		for line in data:
			if line.startswith('\t'):
				currentPageLines.append(line.lstrip().split('\t'))
			else:
				if currentPage:
					currentPage.write(currentPageLines, begin=eval(currentPageBegin))
					
				currentPageName, currentPageBegin = line.lstrip().split('\t')
				currentPage = self._guiMngr.getPage(currentPageName)
				currentPageLines = []
		#	Write trailing Page
		if currentPage:
					currentPage.write(currentPageLines, begin=eval(currentPageBegin))
		
		self._schedule.readSettings()
				 

	def saveFile(self):
		filename = filedialog.asksaveasfilename(defaultextension='.pas.',  filetypes=[('PM Schedule Project', '.pas'), ('All types', '.*')]) if not self._workingFile else self._workingFile
		if not filename:
			return False
			
		with open(filename, 'w') as file:
			advPage = self._guiMngr.getPage('Mentor Information')
			file.write('{}\t{}\n'.format(advPage.getName(), (1, 0)))
			self._writePageData(advPage, file, (1, 0))
			
			setPage = self._guiMngr.getPage('Schedule Settings')
			file.write('{}\t{}\n'.format(setPage.getName(), (1, 1)))
			self._writePageData(setPage, file, (1, 1))
		self._workingFile = filename
		return True
		
		
		
	def saveFileAs(self):
		self._workingFile = ''
		self.saveFile()
		
	
	def savePageAs(self, pageId):
		filename = filedialog.asksaveasfilename(defaultextension='.txt.',  filetypes=[('Text File', '.txt'), ('All types', '.*')])
		if not filename:
			return

		with open(filename, 'w') as file:
			page = self._guiMngr.getPage(self._guiMngr.getNotebook().tab(pageId, 'text'))
			self._writePageData(page, file, (0,0), '')
			
			
	def askQuit(self):
		if self._isAltered:
			message = self._askSaveDialog()
			if (message and not self.saveFile()) or message == None:
				return
		quit()
				
				
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _askSaveDialog(self):
		return messagebox.askyesnocancel(message='Save the Current Schedule?', icon='question', title='Save File?')

	def _writePageData(self, page, file, bg, initText='\t'):
		for line in page.readRaw(begin=bg):
			text = initText
			for token in line:
				text+=token+'\t'
			if text.lstrip():
				file.write(text + '\n')
			
