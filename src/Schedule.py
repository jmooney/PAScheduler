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
import bin.tools as tools
from .TimeSlot import *
from .TimeObj import Time
from .Adviser import Adviser
from .NotebookPage import EntryPage
from .EntryFieldArray import InputError


#------------------------------------------------------------------#

class Schedule(object):

	debugDelay = 0


	def __init__(self):
		super().__init__()

		self.dayOrder = []
		self._timeSlots = []
		self._advisers = []

		self._advisingHours = ''
		self._adviserDensity = ''
		self.timeSlotDuration = 15
		self._minBlockHours = 0
		self._maxBlockHours = 0
		self._minBreakHours = 0
		self._minHoursPerWeek = 0

		Time.schedule = self



	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def createSchedule(self):
		if self._timeSlots:
			self.reset()

		settingsPage = self._guiMngr.getPage('Settings')

		try:
			self.timeSlotDuration = settingsPage.read(pos=(3,1))
			self.timeSlotsPerHour = 60/self.timeSlotDuration

			pageIndex = 1;	settingsPage.validate();	self._readSettings()
			pageIndex = 0;	self.getValidAdviserEntries()

		except InputError:
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
		self._writeAdviserSchedule(displayOptions)
		
	def sortAdvisers(self, func):
		self._advisers.sort(key=func)
		self._writeAdviserSchedule(self._guiMngr.getViewOptions())

		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _createTimeSlots(self):
		times = []
		for timeRng in self._advisingHours:
			times = times + timeRng.getEnumeratedTimes()

		densities = []
		for densityRng in self._adviserDensity:
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
		self._readAdvisers()

		for dayRow in self._timeSlots:
			for slot in dayRow:
				competingAdvisers = slot.getCompetingAdvisers()
				if not competingAdvisers:
					slot.getEntry().setInvalid()
					continue

				for i in range(slot.getDensity()):
					if not competingAdvisers:
						continue

					maxAdviser = competingAdvisers[0]
					for adviser in competingAdvisers:
						numPrev, numAfter, breakSize = self._countConsecutiveBlocks(adviser, slot)
						self._calculateNeed(adviser, slot, numPrev, numAfter, breakSize)
						self._calculateGreed(adviser, slot, numPrev)
						if adviser > maxAdviser:
							maxAdviser = adviser

					slot.scheduleAdviser(maxAdviser, self._guiMngr.getViewOptions())
					competingAdvisers.remove(maxAdviser)
					competingAdvisers.sort()
					time.sleep(self.debugDelay)
				
				for adv in competingAdvisers:
					adv.nAvailSlots-=1
			
					
	def _createSchedulePage2(self):
		page = self._guiMngr.createPage('Adviser Schedule', EntryPage, {'numRows':0, 'numCols':0})
		for adviser in self._advisers:
			adviser.consolidateHours()
		
		dayBar = [''] + self.dayOrder
		page.write([dayBar], begin=(0,0))
		
		page.getEntries(pos=(0,0)).get().state(['disabled'])
		for entry in page.getEntries(row=0)[1:]:
			entry.state(['readonly'])
		
		self._advisers.sort(key=lambda x:x.name.partition(' ')[2])
		self._writeAdviserSchedule(self._guiMngr.getViewOptions())
		page.getEntryArray().setColumnWidths([(0, 50)])



	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _readSettings(self):
		settings = self._guiMngr.getPage('Settings').read(col=1)
		self._advisingHours = settings[1]
		self._adviserDensity = settings[2]
		self._minBlockHours = settings[4]
		self._maxBlockHours = settings[5]
		self._minBreakSlots = settings[6]*self.timeSlotsPerHour
		self._maxSlotsPerWeek = settings[7]*self.timeSlotsPerHour


	def _readAdvisers(self):
		entries = self.getValidAdviserEntries()
		for entryRow in entries:
			advData = [entry.get() for entry in entryRow]
			
			advData[4] = advData[4] if advData[4] != None else self._minBlockHours
			advData[5] = advData[5] if advData[5] != None else (self._maxBlockHours+self._minBlockHours)/2
			advData[6] = advData[6] if advData[6] != None else self._maxBlockHours
			advData[4:7] = [d*self.timeSlotsPerHour for d in advData[4:7]]
			
			adviser = Adviser(advData)
			self._addAdviser(adviser)
			
			
	def _writeAdviserSchedule(self, displayOptions):
		for i in range(len(self._advisers)):
			adviser = self._advisers[i]
			
			data = [[adviser.formatStr(**displayOptions)]]
			for day in self.dayOrder:
				data[0].append(adviser.workHoursText[day])
			self._guiMngr.getPage('Adviser Schedule').write(data, begin=(i+1, 0))


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _addAdviser(self, adviser):
		for time in adviser.availability:
			for enumTimeRow in time.getEnumeratedTimes():
				dayIndex = self.dayOrder.index(enumTimeRow[0].getDay())
				dayRow = self._timeSlots[dayIndex]

				for enumTime in enumTimeRow:
					hrIndex = int((enumTime.getHour()-dayRow[0].getTime().getHour()) * self.timeSlotsPerHour)
					dayRow[hrIndex].addCompetingAdviser(adviser)

		self._advisers.append(adviser)


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def getValidAdviserEntries(self):
		adviserPage = self._guiMngr.getPage('Advisers')
		names = adviserPage.read(col=0)[1:]

		endRow = names.index(None)
		if endRow < 0:
			return

		entries = adviserPage.getEntries(begin=(1, 0), end=(endRow, adviserPage.getEntryArray().numCols-1))
		entries.validate()
		return entries


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _calculateNeed(self, adviser, slot, numSlotsPrev, numSlotsAfter, breakSize):
		personalNeed = tools.pos(adviser.minSlots-adviser.nSchedSlots) + tools.pos(adviser.minSlots-adviser.nAvailSlots)

		possibleConsecSize = numSlotsPrev+1+numSlotsAfter
		if breakSize and breakSize < self._minBreakSlots:
			adviser.need = -1
		if possibleConsecSize < adviser.minSlots:
			adviser.need = -1
		elif numSlotsPrev >= adviser.maxSlots or numSlotsPrev >= self._maxSlotsPerWeek:
			adviser.need = -1
		elif numSlotsPrev > 0 and numSlotsPrev < adviser.minSlots:
			adviser.need = 999
		else:
			adviser.need = personalNeed


	def _calculateGreed(self, adviser, slot, numSlotsPrev):
		A = 1.2;	B = 1.0;	C = 1.0;	D = 1.5;	E=3;

		nSameMajors = len([adv for adv in slot.getScheduledAdvisers() if adv.major == adviser.major])
		avgExp = tools.getAverage([adv.year for adv in slot.getScheduledAdvisers()] + [adviser.year])

		personalGreed = A*tools.pos(slot.getDensity()-nSameMajors) + B*(-math.fabs(2.5 - avgExp)) + \
						C*tools.pos(adviser.reqSlots-adviser.nSchedSlots) + D*tools.pos(adviser.reqSlots-adviser.nAvailSlots)

		slotGreed = 0
		if numSlotsPrev > 0 and numSlotsPrev < adviser.reqSlots:
			slotGreed = E
		elif numSlotsPrev > adviser.reqSlots:
			slotGreed = -E

		adviser.greed = personalGreed + slotGreed


	def _countConsecutiveBlocks(self, adviser, slot):
		numPrev = 0;	tempSlot = slot
		while tempSlot.prev and adviser in tempSlot.prev.getScheduledAdvisers():
			numPrev+=1
			tempSlot = tempSlot.prev

		numAfter = 0;	tempSlot = slot
		while tempSlot.next and adviser in tempSlot.next.getCompetingAdvisers():
			numAfter+=1
			tempSlot = tempSlot.next

		breakSize=0;	tempSlot=slot
		while tempSlot.prev and not adviser in tempSlot.prev.getScheduledAdvisers():
			breakSize+=1
			tempSlot=tempSlot.prev

		return numPrev, numAfter, breakSize



	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def setGui(self, gm):
		self._guiMngr = gm

	def reset(self):
		self.dayOrder = []
		self._timeSlots = []
		self._advisers = []

		self._advisingHours = ''
		self._adviserDensity = ''
		self.timeSlotDuration = 15
		self._minBlockHours = 0
		self._maxBlockHours = 0
		self._minBreakHours = 0
		self._minHoursPerWeek = 0

