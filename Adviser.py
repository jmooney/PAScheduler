'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - Adviser
	
	Description:
		Maintains adviser-specific data and methods in scheduling.
		
'''


# Imports
from TimeObj import Time


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
		self.workHoursText = {}
		self.scheduledTimes = []
		self.consolidatedTimes = []
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def consolidateHours(self):
		if not self.scheduledTimes:
			return
		
		dayHrData 	 = []
		hoursInRange = []
		prevSlot 		 = None
		currentDay 	 = self.scheduledTimes[0].getDay()
		
		for timeSlot in self.scheduledTimes:
			time = timeSlot.getTime()
			day = timeSlot.getDay()
			
			if not prevSlot or timeSlot == prevSlot.next:
				hoursInRange.append(time.getHour())
				
			else:
				dayHrData.append(Time( ([currentDay], hoursInRange) ))
				hoursInRange = [time.getHour()]
			
				if day != currentDay:
					currentDay = day
					self.consolidatedTimes.append(dayHrData)
					dayHrData = []
			
			prevSlot = timeSlot
		
		if hoursInRange:
			newTime = Time( ([currentDay], hoursInRange) )
			dayHrData.append(Time( ([currentDay], hoursInRange) ))
			
		if dayHrData:
			self.consolidatedTimes.append(dayHrData)
		
		for day in Time.schedule.dayOrder:
			self.workHoursText[day] = ''
			
		for day in self.consolidatedTimes:
			text = ''
			for timeRng in day:
				text += timeRng.format(hour=True, time='Condensed', range=True) + " "
			self.workHoursText[timeRng.getDay()] = text

		
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getShortName(self):
		first, temp, last = self.name.partition(' ')
		return '{} {}. '.format(first, last[0])
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def __lt__(self, otherAdviser):
		if self.need == otherAdviser.need:
			return self.greed < otherAdviser.greed
		else:
			return self.need < otherAdviser.need
			
