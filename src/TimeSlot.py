'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - TimeSlot
	
	Description:
		Maintains data specific to one scheduleable slot. Provides methods for updating/changing scheduled advisors.
		
'''

# Imports
from tkinter import END


#------------------------------------------------------------------#

class TimeSlot(object):
	
	def __init__(self, time, density, prev):
		super().__init__()
		
		self._time = time
		self._density = density
		self._competingAdvisors = []
		self._scheduledAdvisors = []
		
		self.next = None
		self.prev = prev
		if prev:
			prev.next = self
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def scheduleAdvisor(self, advisor, options):
		advisor.nSchedSlots += 1
		advisor.scheduledTimes.append(self)
		
		self._scheduledAdvisors.append(advisor)
		self._entry.insert(0, advisor.formatStr(**options) + ' ')
		self._entry.update_idletasks()
	
	
	def displayText(self, fmtOptions):
		text = ''
		for adv in self._scheduledAdvisors:
			text += adv.formatStr(**fmtOptions) + ' '
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
		
	def addCompetingAdvisor(self, adv):
		adv.nAvailSlots += 1
		self._competingAdvisors.append(adv)
	def getCompetingAdvisors(self):
		return self._competingAdvisors
	def getScheduledAdvisors(self):
		return self._scheduledAdvisors
		
