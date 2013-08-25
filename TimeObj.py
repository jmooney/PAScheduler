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
		if options.get('range'):
			options['range'] = False
			
			tempOptions = options.copy()
			tempOptions.update({'_isRngEnd':True, '_hourIndex':-1})
			
			return '{}-{}'.format(self.format(**options), self.format(**tempOptions))
			
		if options.get('day'):
			return self.getDay()
			
		elif options.get('hour'):
			hourIndex = options.get('_hourIndex', 0)
			hour = self._hours[hourIndex]
			
			if options.get('time') == 'Standard':
				secondDigit = int(hour%1*self.minsPerHour) + (self.schedule.timeSlotDuration if options.get('_isRngEnd') else 0)
				firstDigit = int(hour)
				
				if secondDigit >= 60:
					firstDigit += int(secondDigit/60)
					secondDigit = int(secondDigit%60 * self.minsPerHour)
				if firstDigit > 12:
					firstDigit = firstDigit-12
					
				needSD = options.get('_needSecondDigit', True) or secondDigit
				
				firstDigit = str(firstDigit)
				concatChar = ':' if needSD else ''
				secondDigit = '{0:0=2d}'.format( secondDigit ) if needSD else ''
				endChar = 'a' if hour < 12 else 'p'
				endChar = endChar if needSD else ''
				
				return '{}{}{}{}'.format(firstDigit, concatChar, secondDigit, endChar)
				
			elif options.get('time') == 'Condensed':
				options['time'] = 'Standard';	options['_needSecondDigit']=False
				return self.format(**options)
				
			else:
				return str(int(self._hours[0]))
				
	
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
		
