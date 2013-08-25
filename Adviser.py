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
		self.year 			= data[2]
		self.minSlots 	= data[3]
		self.reqSlots 	= data[4]
		self.maxSlots 	= data[5]
		self.availability = data[6]
		
		self.nSchedSlots = 0
		self.nAvailSlots = 0
		self.scheduledTimes = []
		self.scheduledTimesDict = {}
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def consolidateTimes(self):
		if not self.scheduledTimes:
			return
			
		for day in self.scheduledTimes[0].getTime().schedule._dayOrder:
			self.scheduledTimesDict[day] = []
	
		return
		
		index = 0
		currentSlot = startSlot = self.scheduledTimes[0]
		currentDay = currentSlot.getDay()
		
		while index < len(self.scheduledTimes)-1:
			nextSlot = self.scheduledTimes[index+1]
			
			if currentSlot.next != nextSlot:
				print(currentSlot.getDay(), nextSlot.getDay())
				
				endSlot = currentSlot
				self.scheduledTimesDict[currentDay].append('{}-{}'.format( \
					startSlot.getTime().format(hour=True, time='Standard'), endSlot.getTime().format(hour=True, end=True, time='Standard')))
				
				startSlot=nextSlot
				if startSlot.getDay() != currentDay:
					currentDay = startSlot.getDay()
					self.scheduledTimesDict[currentDay] = []
					
			currentSlot = nextSlot
			index+=1
			
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def __lt__(self, otherAdviser):
		if self.need == otherAdviser.need:
			return self.greed < otherAdviser.greed
		else:
			return self.need < otherAdviser.need
			
