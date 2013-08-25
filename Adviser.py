'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - Adviser
	
	Description:
		Maintains adviser-specific data and methods in scheduling.
		
'''


# Imports



#------------------------------------------------------------------#

class Adviser(object):

	def __init__(self, data):
		super().__init__()
		
		self.name 		= data[0]
		self.major 		= data[1]
		self.year 		= data[2]
		self.minSlots 	= data[3]
		self.reqSlots 	= data[4]
		self.maxSlots 	= data[5]
		self.availability = data[6]
		
		self.nSchedSlots = 0
		self.nAvailSlots = 0
		self.scheduledTimes = []
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def __lt__(self, otherAdviser):
		if self.need == otherAdviser.need:
			return self.greed < otherAdviser.greed
		else:
			return self.need < otherAdviser.need
			
