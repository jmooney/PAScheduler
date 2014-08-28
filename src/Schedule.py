'''

	Author:	John Mooney
	Date:		07/16/2013

	PAScheduler 2 - Schedule

	Description:
		Maintains schedule-specific data and methods.

'''


# Imports
import math
import time
import src.tools as tools
from .TimeSlot import *
from .TimeObj import Time
from .Advisor import Advisor
from .NotebookPage import EntryPage
from .EntryFieldArray import InputError


#------------------------------------------------------------------#

class Schedule(object):

	debugDelay = 0


	def __init__(self):
		super().__init__()

		self.dayOrder = []
		self._timeSlots = []
		self._advisors = []

		self._advisingHours = ''
		self._advisorDensity = ''
		self.timeSlotDuration = 15
		self._minBlockSlots = 0
		self._maxBlockSlots = 0
		self._minBreakSlots = 0
		self._minSlotsPerWeek = 0
		self._maxSlotsPerWeek = 0

		Time.schedule = self



	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def createSchedule(self):
		if self._timeSlots:
			self.reset()

		settingsPage = self._guiMngr.getPage('Schedule Settings')

		try:
			self.timeSlotDuration = settingsPage.read(pos=(3,1))
			self.timeSlotsPerHour = 60/self.timeSlotDuration

			pageIndex = 1;	settingsPage.validate();	self._readSettings()
			pageIndex = 0;	self.getValidAdvisorEntries()

		except ValueError:
			self._guiMngr.getNotebook().select(self._guiMngr.getNotebook().tabs()[pageIndex])
			return

		self._createTimeSlots()
		self._createSchedulePage1()
		self._fillSchedule()
		self._createSchedulePage2()
		
		
	def updateText(self):
		displayOptions = self._guiMngr.getViewOptions()
		for row in self._timeSlots:
			for slot in row:
				slot.displayText(displayOptions)
		self._writeAdvisorSchedule(displayOptions)
		
	def sortAdvisors(self, func):
		self._advisors.sort(key=func)
		self._writeAdvisorSchedule(self._guiMngr.getViewOptions())

		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _createTimeSlots(self):
		times = []
		for timeRng in self._advisingHours:
			times = times + timeRng.getEnumeratedTimes()

		densities = []
		for densityRng in self._advisorDensity:
			for day in densityRng.getDays():
				densities.append(densityRng.getDensity())

		for dayIndex in range(len(times)):
			self.dayOrder.append(times[dayIndex][0].getDay())

			row = []
			for i in range(len(times[dayIndex])):
				row.append(TimeSlot(times[dayIndex][i], densities[dayIndex], row[i-1] if i-1>=0 else None))
			self._timeSlots.append(row)


	def _createSchedulePage1(self):
		page = self._guiMngr.createPage('Schedule', EntryPage, {'numRows':0, 'numCols':0})

		timeBar = []
		for timeSlot in max(self._timeSlots, key=len):
			timeBar.append(timeSlot.getHour(mt=False))
		dayBar = [[day] for day in self.dayOrder]

		page.write([timeBar], begin=(0, 1))
		page.getEntryArray().setColumnWidths([(i+1, 30) for i in range(len(timeBar))])
		
		page.write(dayBar, begin=(1, 0))
		page.getEntryArray().setColumnWidths([(0, 10)])
		
		for dayIndex in range(len(self._timeSlots)):
			dayRow = self._timeSlots[dayIndex]

			for slotIndex in range(len(dayRow)):
				slot = dayRow[slotIndex]

				entryPos = (dayIndex+1, timeBar.index(slot.getHour(mt=False)) + 1)
				slot.setEntry(page.getEntries(pos=entryPos).get())

		page.getEntries(pos=(0, 0))._entries.state(['disabled'])
		for entry in page.getEntries(row=0):
			entry.state(['readonly'])
		for entry in page.getEntries(col=0):
			entry.state(['readonly'])
		self._guiMngr.getNotebook().select(self._guiMngr.getNotebook().tabs()[-1])
		self._guiMngr.getNotebook().update_idletasks()
		

	def _fillSchedule(self):
		self._readAdvisors()
		
		for dayRow in self._timeSlots:
			for slot in dayRow:
				competingAdvisors = slot.getCompetingAdvisors()[:]
				
				for i in range(slot.getDensity()):
					if not competingAdvisors:
						continue

					maxAdvisor = competingAdvisors[0]
					doMax = False
					for advisor in competingAdvisors:
						numPrev, numAfter, breakSize = self._countConsecutiveBlocks(advisor, slot)
						self._calculateNeed(advisor, slot, numPrev, numAfter, breakSize)
						self._calculateGreed(advisor, slot, numPrev)
						if advisor > maxAdvisor:
							maxAdvisor = advisor
					
					if maxAdvisor.need >= 0:
						slot.scheduleAdvisor(maxAdvisor, self._guiMngr.getViewOptions())
					competingAdvisors.remove(maxAdvisor)
					competingAdvisors.sort()
					time.sleep(self.debugDelay)
				
				for adv in competingAdvisors:
					adv.nAvailSlots-=1
				if not slot.getScheduledAdvisors():
					slot.getEntry().setInvalid()
			
					
	def _createSchedulePage2(self):
		page = self._guiMngr.createPage('Advisor Schedule', EntryPage, {'numRows':0, 'numCols':0})
		for advisor in self._advisors:
			advisor.consolidateHours()
		
		dayBar = [''] + self.dayOrder
		page.write([dayBar], begin=(0,0))
		
		page.getEntries(pos=(0,0)).get().state(['disabled'])
		for entry in page.getEntries(row=0)[1:]:
			entry.state(['readonly'])
		
		self._advisors.sort(key=lambda x:x.name.partition(' ')[2])
		self._writeAdvisorSchedule(self._guiMngr.getViewOptions())
		page.getEntryArray().setColumnWidths([(0, 50)])



	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _readSettings(self):
		settings = self._guiMngr.getPage('Schedule Settings').read(col=1)
		self._advisingHours = settings[1]
		self._advisorDensity = settings[2]
		self._minBlockSlots = settings[4]*self.timeSlotsPerHour
		self._maxBlockSlots = settings[5]*self.timeSlotsPerHour
		self._minBreakSlots = settings[6]*self.timeSlotsPerHour
		self._minSlotsPerWeek = settings[7]*self.timeSlotsPerHour
		self._maxSlotsPerWeek = settings[8]*self.timeSlotsPerHour


	def _readAdvisors(self):
		entries = self.getValidAdvisorEntries()
		for entryRow in entries:
			advData = [entry.get() for entry in entryRow]
			advData[4] = advData[4]*self.timeSlotsPerHour if advData[4] != None else self._minSlotsPerWeek
			advData[5] = advData[5]*self.timeSlotsPerHour if advData[5] != None else (self._maxSlotsPerWeek+self._maxSlotsPerWeek)/2
			advData[6] = advData[6]*self.timeSlotsPerHour if advData[6] != None else self._maxSlotsPerWeek
				
			advisor = Advisor(advData)
			self._addAdvisor(advisor)
			
			
	def _writeAdvisorSchedule(self, displayOptions):
		for i in range(len(self._advisors)):
			advisor = self._advisors[i]
			
			displayOptions.update({'pageOption':'page2'})
			data = [[advisor.formatStr(**displayOptions)]]\
			
			for day in self.dayOrder:
				data[0].append(advisor.workHoursText[day])
			self._guiMngr.getPage('Advisor Schedule').write(data, begin=(i+1, 0))


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _addAdvisor(self, advisor):
		for time in advisor.availability:
			for enumTimeRow in time.getEnumeratedTimes():
				dayIndex = self.dayOrder.index(enumTimeRow[0].getDay())
				dayRow = self._timeSlots[dayIndex]

				for enumTime in enumTimeRow:
					hrIndex = int((enumTime.getHour()-dayRow[0].getTime().getHour()) * self.timeSlotsPerHour)
					dayRow[hrIndex].addCompetingAdvisor(advisor)

		self._advisors.append(advisor)


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def getValidAdvisorEntries(self):
		advisorPage = self._guiMngr.getPage('Mentor Information')
		names = advisorPage.read(col=0)[1:]

		endRow = names.index(None)
		if endRow < 0:
			return

		entries = advisorPage.getEntries(begin=(1, 0), end=(endRow, advisorPage.getEntryArray().numCols-1))
		entries.validate()
		return entries


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _calculateNeed(self, advisor, slot, numSlotsPrev, numSlotsAfter, breakSize):
		personalNeed = tools.pos(advisor.minSlotsPerWeek-advisor.nSchedSlots)
		
		possibleConsecSize = numSlotsPrev+1+numSlotsAfter
		if breakSize and breakSize < self._minBreakSlots:
			advisor.need = -1
		elif possibleConsecSize < self._minBlockSlots:
			advisor.need = -1
		elif numSlotsPrev+1 > self._maxBlockSlots:
			advisor.need = -1
		elif numSlotsPrev+1 > advisor.maxSlotsPerWeek:
			advisor.need = -1
		elif numSlotsPrev > 0 and numSlotsPrev < advisor.minSlotsPerWeek:
			advisor.need = 999
		else:
			advisor.need = personalNeed


	def _calculateGreed(self, advisor, slot, numSlotsPrev):
		A = 15;	B = 1.2;	C = 1.0;	D = 1.0;	E = 1.5;	F=3;	

		nSameMajors = len([adv for adv in slot.getScheduledAdvisors() if adv.major == advisor.major])
		avgExp = tools.getAverage([adv.year for adv in slot.getScheduledAdvisors()] + [advisor.year])

		personalGreed = A*tools.pos(advisor.minSlotsPerWeek-advisor.nAvailSlots) + B*tools.pos(slot.getDensity()-nSameMajors) + \
						C*(-math.fabs(2.5 - avgExp)) + D*tools.pos(advisor.reqSlotsPerWeek-advisor.nSchedSlots) + \
						E*tools.pos(advisor.reqSlotsPerWeek-advisor.nAvailSlots)

		slotGreed = 0
		if numSlotsPrev > 0 and numSlotsPrev < advisor.reqSlotsPerWeek:
			slotGreed = F
		elif numSlotsPrev > advisor.reqSlotsPerWeek:
			slotGreed = -F

		advisor.greed = personalGreed + slotGreed


	def _countConsecutiveBlocks(self, advisor, slot):
		numPrev = 0;	tempSlot = slot
		while tempSlot.prev and advisor in tempSlot.prev.getScheduledAdvisors():
			numPrev+=1
			tempSlot = tempSlot.prev

		numAfter = 0;	tempSlot = slot
		while tempSlot.next and advisor in tempSlot.next.getCompetingAdvisors():
			numAfter+=1
			tempSlot = tempSlot.next

		breakSize=0;	tempSlot=slot
		while tempSlot.prev and not advisor in tempSlot.prev.getScheduledAdvisors():
			breakSize+=1
			tempSlot=tempSlot.prev
		if not tempSlot.prev:
			breakSize = 0

		return numPrev, numAfter, breakSize



	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def setGui(self, gm):
		self._guiMngr = gm

	def reset(self):
		self.dayOrder = []
		self._timeSlots = []
		self._advisors = []

		self._advisingHours = ''
		self._advisorDensity = ''
		self.timeSlotDuration = 15
		self._minBlockSlots = 0
		self._maxBlockSlots = 0
		self._minBreakHours = 0
		self._minHoursPerWeek = 0

