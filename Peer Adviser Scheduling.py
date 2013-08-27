'''

	Author:	John Mooney
	Date:	07/16/2013
	
	PAScheduler 2 - Main
	
	Description:
		The Main entry point for the Peer Adviser Scheduler
		
'''

# Imports

from FileManager import *
from GuiManager import *
from Schedule2 import *
from EntryFieldArray import TypedEntry


#------------------------------------------------------------------#

def main():

	schedule 		= Schedule()
	gm 					= GuiManager(schedule)
	fileManager 	= FileManager(gm, schedule)
	
	window = gm.createWindow(fileManager)

	schedule.setGui(gm)
	TypedEntry.createStyle()
	
	window.mainloop()
	
main()