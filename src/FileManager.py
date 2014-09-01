
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
		self._workingFile 	= "Untitled"
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def newFile(self):
		if not self._askSaveFile():
			return
		
		self._guiMngr.reset()
		self._schedule.reset()
		self._workingFile = "Untitled"
		
		
		
	def openFile(self):
		if not self._askSaveFile():
			return
			
		filename = filedialog.askopenfilename(defaultextension='.pas', filetypes=[('PA Schedule Project', '.pas'), ('All types', '.*')])
		if not filename:
			return
		
		self._guiMngr.reset()
		self._schedule.reset()
			
		self._workingFile = filename
		with open(filename, 'r') as file:
			#self._readMetadata(file)
			data = [line.rstrip() for line in file.readlines() if line.rstrip()]
		
		currentPage = None
		currentPageLines = []
		for line in data:
			if line.startswith('\t'):	#Bug is here. Ignores 'double tab' separating an empty column
				currentPageLines.append(line.lstrip().split('\t'))
			else:
				if currentPage:
					print(str(currentPageLines) + '\n\n')
					currentPage.write(currentPageLines, begin=eval(currentPageBegin))
					
				currentPageName, currentPageBegin = line.lstrip().split('\t')
				currentPageLines = []
				
				currentPage = None
				if currentPageName in self._guiMngr.getPages():
					currentPage = self._guiMngr.getPage(currentPageName)
				else:
					currentPage = self._guiMngr.createPage(currentPageName)
					
		#	Write trailing Page
		if currentPage:
					currentPage.write(currentPageLines, begin=eval(currentPageBegin))
		
		self._schedule.readSettings()
				 

	def saveFile(self):
		filename = filedialog.asksaveasfilename(defaultextension='.pas.',  filetypes=[('PM Schedule Project', '.pas'), ('All types', '.*')]) if not self._workingFile else self._workingFile
		if not filename:
			return False
			
		with open(filename, 'w') as file:
			#self._writeMetadata(file)
			
			pageBegins = [(1, 0), (1, 1)]
			for i in range(len(self._guiMngr.getPages())):
				pageName = self._guiMngr.getPageName(i)
				pageBegin = pageBegins[i] if i < len(pageBegins) else (0, 0)
				page = self._guiMngr.getPage(pageName)
				
				file.write('{}\t{}\n'.format(pageName, pageBegin))
				self._writePageData(page, file, pageBegin)
			
			
			
			
			#advPage = self._guiMngr.getPage('Mentor Information')
			#file.write('{}\t{}\n'.format(advPage.getName(), (1, 0)))
			#self._writePageData(advPage, file, (1, 0))
			
			#setPage = self._guiMngr.getPage('Schedule Settings')
			#file.write('{}\t{}\n'.format(setPage.getName(), (1, 1)))
			#self._writePageData(setPage, file, (1, 1))
			
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
	
	def _askSaveFile(self):
		if self._isAltered:
			message = self._askSaveDialog()
			if (message and not self.saveFile()) or message == None:
				return False
		return True
				
	def _askSaveDialog(self):
		return messagebox.askyesnocancel(message='Save Project ' + self._workingFile + '?', icon='question', title='Save File?')

	def _writePageData(self, page, file, bg, initText='\t'):
		for row in page.readRaw(begin=bg):
			text = initText
			for col in row:
				text+=colno+'\t'
			if text.lstrip():
				file.write(text + '\n')
			
