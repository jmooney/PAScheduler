'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - TimeSlot
	
	Description:
		Maintains data specific to one scheduleable slot. Provides methods for updating/changing scheduled advisers.
		
'''

# Imports
from tkinter import END

#------------------------------------------------------------------#

class TimeSlot(object):
	
	def __init__(self, time, density, prev):
		super().__init__()
		
		self._time = time
		self._density = density
		self._competingAdvisers = []
		self._scheduledAdvisers = []
		
		self.next = None
		self.prev = prev
		if prev:
			prev.next = self
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def scheduleAdviser(self, adviser):
		adviser.nSchedSlots += 1
		adviser.scheduledTimes.append(self)
		
		self._scheduledAdvisers.append(adviser)
		self._entry.insert(0, adviser.getShortName())
		self._entry.update_idletasks()
	
	
	def displayText(self, func):
		text = ''
		for adv in self._scheduledAdvisers:
			text += str(func(adv)) + ' '
		self._entry.delete(0, END)
		self._entry.insert(0, text)
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getTime(self):
		return self._time
	def getDay(self):
		return self._time.format(day=True)
	def getHour(self, mt=True):
		return self._time.format(hour=True, time='Standard')
	def getDensity(self):
		return self._density
	
	def setEntry(self, e):
		self._entry = e
	def getEntry(self):
		return self._entry
		
	def addCompetingAdviser(self, adv):
		adv.nAvailSlots += 1
		self._competingAdvisers.append(adv)
	def getCompetingAdvisers(self):
		return self._competingAdvisers
	def getScheduledAdvisers(self):
		return self._scheduledAdvisers
		
