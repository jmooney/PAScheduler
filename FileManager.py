
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


#-----------------------------------------------------#

class FileManager(object):

	def __init__(self, guiMngr, schedule):
		self._guiMngr 		= guiMngr
		self._schedule 	= schedule
		self._isAltered 	= True
		self._workingFile = ""
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def newFile(self):
		if self._isAltered:
			message = self._askSaveDialog()
			if message == 'yes':
				self.saveFile()
			elif message == 'cancel':
				return
		
		self._guiMngr.reset()
		self._schedule.reset()
		self._workingFile = ""
		
		
		
	def openFile(self):
		if self._isAltered:
			message = self._askSaveDialog()
			if message == 'yes':
				self.saveFile()
			elif message == 'cancel':
				return
			
		self._guiMngr.reset()
		self._schedule.reset()
		
		filename = filedialog.askopenfilename(defaultextension='.txt.', filetypes=[('all files', '.*'), ('text files', '.txt')])
		if not filename:
			return
			
		with open(filename, 'r') as file:
			data = [line.rstrip() for line in file.readlines() if line]
		
		currentPage = None
		currentPageLines = []
		for line in data:
			print("Line : ", line)
			if line.startswith('\t'):
				currentPageLines.append(line.lstrip().split('\t'))
			else:
				if currentPage:
					currentPage.write(currentPageLines, begin=eval(currentPageBegin))
					currentPage=None
				else:
					currentPageName, currentPageType, currentPageBegin, currentPageInits = line.lstrip().split('\t')
					try:
						currentPage = self._guiMngr.getPage(currentPageName)
					except KeyError:
						currentpage = self._guiMngr.createPage(currentPageName, eval(currentPageType), eval(currentPageInits))
					

				 

	def saveFile(self):
		filename = filedialog.asksaveasfilename(defaultextension='.txt.',  filetypes=[('all files', '.*'), ('text files', '.txt')]) if not self._workingFile else self._workingFile
		if not filename:
			return
			
		with open(filename, 'w') as file:
			for page in self._guiMngr.getPages().values():
				file.write('{}\t{}\t{}\t{}\n'.format(page.getName(), page.getType(), page.getWriteBegin(), page.getCreationInits()))
				
				for line in page.readRaw(begin=page.getWriteBegin()):
					text = '\t'
					for token in line:
						text+=token+'\t'
				
					if text.lstrip():
						file.write(text + '\n')
				
				file.write('\n')
				
		self._workingFile = filename
		
		
		
	def saveFileAs(self):
		self._workingFile = ''
		self.saveFile()
		

	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _askSaveDialog(self):
		return messagebox.askyesnocancel(message='Save the Current Schedule?', icon='question', title='Save File?')
		

		