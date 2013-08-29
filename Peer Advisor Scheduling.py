'''

	Author:	John Mooney
	Date:	07/16/2013
	
	PAScheduler 2 - Main
	
	Description:
		The Main entry point for the Peer Advisor Scheduler
		
'''

# Imports
from src.FileManager import *
from src.GuiManager import *
from src.Schedule import *
from src.EntryFieldArray import TypedEntry


#------------------------------------------------------------------#

def main():

	schedule 		= Schedule()
	gm 				= GuiManager(schedule)
	fileManager 	= FileManager(gm, schedule)
	
	window = gm.createWindow(fileManager)

	schedule.setGui(gm)
	TypedEntry.createStyle()
	
	window.mainloop()
	
main()