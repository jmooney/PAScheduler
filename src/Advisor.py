'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - Advisor
	
	Description:
		Maintains advisor-specific data and methods in scheduling.
		
'''


# Imports
from .TimeObj import Time


#------------------------------------------------------------------#

class Advisor(object):

	def __init__(self, data):
		super().__init__()
		
		self.name 	= data[0]
		self.email	= data[1]
		self.major 	= data[2]
		self.returning 	= data[3]
		self.minSlotsPerWeek = data[4]
		self.reqSlotsPerWeek = data[5]
		self.maxSlotsPerWeek = data[6]
		self.availability = data[7]
		
		self.nSchedSlots = 0
		self.nAvailSlots = 0
		self.nAvailSlotsRem = 0
		self.scheduledTimes = []
		self.consolidatedTimes = []
	
		self.workHoursText = {}
		for day in Time.schedule.dayOrder:
			self.workHoursText[day] = ''
			
			
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def consolidateHours(self):
		if not self.scheduledTimes:
			return
		
		dayHrData 	 = []
		hoursInRange = []
		prevSlot 	 = None
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
			
		for day in self.consolidatedTimes:
			text = ''
			for timeRng in day:
				text += timeRng.format(hour=True, time='Standard', range=True) + " "
			self.workHoursText[timeRng.getDay()] = text

		
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def formatStr(self, **options):
		firstName = self.name.partition(' ')[0]
		lastName = self.name.partition(' ')[2]

		text = ''
		nameType = options.get('name')
		if nameType == 'first':
			if options.get('pageOption') == 'page2':
				text = '{} {}'.format(firstName, lastName)
			else:
				text = '{} {}.'.format(firstName, lastName[0])
				
		elif nameType == 'last':
			if options.get('pageOption') == 'page2':
				text = '{}, {}'.format(lastName, firstName)
			else:
				text = '{}, {}.'.format(lastName, firstName[0])
				
				
		if options.get('major'):
			text += ' ({})'.format(self.major)
		if options.get('email'):
			text += ' ' + self.email
		if options.get('returning'):
			text += ' ' + str(self.returning)
			
		if not text:
				return self.formatStr(name='last', pageOption=options.get('pageOption'))
		return text
		
		
	def getTotalHours(self):
		return self.nSchedSlots / Time.schedule.timeSlotsPerHour
	def getAvailableHours(self):
		return self.nAvailSlots / Time.schedule.timeSlotsPerHour


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def __lt__(self, otherAdvisor):
		if self.need == otherAdvisor.need:
			return self.greed < otherAdvisor.greed
		else:
			return self.need < otherAdvisor.need
			
