'''

	Author:	John Mooney
	Date:		08/05/2013
	
	PAScheduler 2 - Time
	
	Description:
		Converts various representations of time amongst each other. Ex string to military time etc..
		
'''

# Imports
import re
from tools import frange


#---------------------------------------------------------------#

class InputObject(object):

	def __init__(self, data):
		super().__init__()
		
		if isinstance(data, str):
			self._parseDescription(data)
		else:
			self._extractData(data)

			
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
			
	def _parseDescription(self, desc):
		if not re.match(self.grammarDescriptor, desc):
			raise ValueError('Invalid Input for ' + str(self.__class__) + ' Object')
			
	def _extractData(self):
		raise NotImplementedError
		
		
		
#---------------------------------------------------------------#

class _DayRngInputObject(InputObject):
	
	daysOfTheWeek = ['M', 'T', 'W', 'Th', 'F', 'S', 'Su']

	dayDescriptor = '([a-zA-Z]+)'
	rangeFmtDescriptor = '{desc}(?:-{desc})?'
	dayRangeDescriptor = rangeFmtDescriptor.format(desc=dayDescriptor)
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def _parseDescription(self, desc):
		super()._parseDescription(desc)
		
		desc = desc.lstrip().partition(' ')
		dayDesc = desc[0]
		otherDesc = desc[2]
		
		self._days = re.findall(self.dayRangeDescriptor, dayDesc)[0]
		self._enumerateDays()
		self._parseDesc2ndToken(otherDesc)
	

	def _parseDesc2ndToken(self, desc):
		raise NotImplementedError()

	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def _enumerateDays(self):
		dayRange = self._days
		if not dayRange[1]:
			self._days = [dayRange[0]]
			return
		
		beginIndex = self.daysOfTheWeek.index(dayRange[0])
		endIndex = self.daysOfTheWeek.index(dayRange[1])
		
		if endIndex <= beginIndex:
			raise ValueError('Invalid Day Range on Time Value')
		else:
			self._days = self.daysOfTheWeek[beginIndex:endIndex+1]
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	@classmethod
	def getArrayDivider(cls):
		return ';'		
	def getDays(self):
		return self._days[:]
	def getDay(self):
		return self._days[0]
		

		
#---------------------------------------------------------------#
		
class DayDensity(_DayRngInputObject):
	
	grammarFmtDescriptor = '^\\s*{0}\\s+(\\d+)\\s*$'
	grammarDescriptor = grammarFmtDescriptor.format(_DayRngInputObject.dayRangeDescriptor)
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _parseDesc2ndToken(self, densDesc):
		self._density = int(densDesc)
	def getDensity(self):
		return self._density
		
		
		
#---------------------------------------------------------------#
		
class Time(_DayRngInputObject):
	
	schedule = None
	minsPerHour = 60
	
	'''	Create Regex-Descriptors	'''
	hourDescriptor = '(\\d+(?::\\d+)?)([ap])?'
	hourRangeDescriptor = _DayRngInputObject.rangeFmtDescriptor.format(desc=hourDescriptor)

	grammarFmtDescriptor = '^\\s*{0}\\s+({1}\\s+)*{1}\\s*$'
	grammarDescriptor = grammarFmtDescriptor.format(_DayRngInputObject.dayRangeDescriptor, hourRangeDescriptor)
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _extractData(self, data):
		self._days = data[0]
		self._hours = data[1]
		
		if not self._days and self._hours:
			raise ValueError("Time Value requires a description string('text') or a 'days' and 'hours' list of values")
			
			
	def _parseDesc2ndToken(self, hourDesc):
		hourRanges = re.findall(self.hourRangeDescriptor, hourDesc)
		self._hours = self._extractMilitaryTimes(hourRanges)
		self._enumerateHours()
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def format(self, **options):
		if options.get('day'):
			return self.getDay()
		elif options.get('hour'):
			if options.get('time') == 'Standard':
				return  str(int(self._hours[0])) + ':' + \
					"{0:0=2d}".format(int(self._hours[0]%1*self.minsPerHour) + (self.schedule.timeSlotDuration if options.get('end') else 0)) + \
					('a' if self._hours[0] < 12 else 'p')
				
	
	def getEnumeratedTimes(self):
		enumeratedTimes = []
		
		for day in self._days:
			row = []	
			for hour in self._hours:
				row.append( Time(([day], [hour])) )
			enumeratedTimes.append(row)
		return enumeratedTimes
		
			
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''			

	def _enumerateHours(self):
		hourRanges = self._hours
		
		hours = []
		for hourRange in hourRanges:
			if not hourRange[1]:
				hours.append(hourRange[0])
			else:
				beginHour = hourRange[0]
				endHour = hourRange[1]
				
				if endHour <= beginHour:
					raise ValueError('Invalid Hour Range on Time Value')
				else:
					hours = hours + [hour for hour in frange(beginHour, endHour, self.schedule.timeSlotDuration/self.minsPerHour)]
					
		self._hours = hours
	
	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def _extractMilitaryTimes(self, hourRanges):
		hourRngs = []
		for hrRange in hourRanges:
			
			hours = []
			hours.append(self._getMilitaryTime(hrRange[0], hrRange[1]))
			hours.append(self._getMilitaryTime(hrRange[2], hrRange[3]))
			
			hourRngs.append(hours)
		return hourRngs
		
	
	@classmethod
	def _getMilitaryTime(cls, hour, char):
		if not hour:
			return None
			
		hour=hour.split(':')
		
		hr = int(hour[0])
		if len(hour) > 1:
			hr += int(hour[1])/cls.minsPerHour
		if char=='p' or hr < 8:
			hr += 12
		
		return hr
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''	
	
	def getHours(self):
		return self._hours[:]
	def getHour(self):
		return self._hours[0]
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''	
	
	def __str__(self):
		return self.format(hour=True, time='Standard')
		
