'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - Schedule
	
	Description:
		Maintains schedule-specific data and methods.
		
'''


# Imports
from TimeSlot import *
from Adviser import Adviser
from NotebookPage import EntryPage
from TimeObj import Time, DayDensity


#------------------------------------------------------------------#

class Schedule(object):

	debugDelay = .5
	
	
	def __init__(self):
		super().__init__()
		
		self._dayOrder = []
		self._timeSlots = []
		self._advisers = []
		
		self._advisingHours = ''
		self._adviserDensity = ''
		self.timeSlotDuration = 0
		self._minBlockHours = 0
		self._maxBlockHours = 0
		self._minBreakHours = 0
		self._minHoursPerWeek = 0
		
		Time.schedule = self
		
	

	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
		
	def setGui(self, guiMngr):
		self._guiMngr = guiMngr
		
		settingsPage = guiMngr.getPage('Settings')
		settingsPage.write('Advising Hours\tM-Th 9-5; F 10-12\n' + \
									'Number of Active Advisers\tM-Th 3; F 2\n' + \
									'Time Slot Duration (minutes)\t15\n' + \
									'Minimum Consecutive Hours\t1\n' + \
									'Maximum Consecutive Hours\t3\n' + \
									'Minimum Consecutibe Break Hours\t1.5\n' + \
									'Maximum Hours per Week\t7', begin=(1,0))
		
		entryTypes = [[Time], [DayDensity], int, float, float, float, float]

		descEntries = settingsPage.getEntries(col=0)
		valueEntries = settingsPage.getEntries(col=1)[1:]
		

		for entry in descEntries:
			entry.state(['readonly'])
		for i in range(len(entryTypes)):
			valueEntries[i].setType(entryTypes[i], True)

			
	def createSchedule(self):
		settingsPage = self._guiMngr.getPage('Settings')
		
		self.timeSlotDuration = settingsPage.read(pos=(3,1))
		self.timeSlotsPerHour = 60/self.timeSlotDuration
		
		settingsPage.validate()
		
		settings = settingsPage.read(col=1)
		self._advisingHours = settings[1]
		self._adviserDensity = settings[2]
		self._minBlockHours = settings[4]
		self._maxBlockHours = settings[5]
		self._minBreakHours = settings[6]
		self._minHoursPerWeek = settings[7]

		self._createTimeSlots()
		self._fillSchedule()
		self._createGUIPage()
		
	
	
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
			self._dayOrder.append(times[dayIndex][0].getDay())
		
			row = []
			for slot in times[dayIndex]:
				row.append(TimeSlot(slot, densities[dayIndex]))
			self._timeSlots.append(row)
		print(self._dayOrder)

		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _fillSchedule(self):
		self._readAdvisers()
		return

		for day in self._timeSlots:
			for slot in day:

				competingAdvisers = slot.getCompetingAdvisers()
				if not competingAdvisers:
					continue

				for i in range(slot.getAdviserDensity()):
					maxAdviser = competingAdvisers[0]

					for adviser in competingAdvisers:
						self._calculateNeed(adviser, slot)
						self._calculateGreed(adviser, slot)
						if adviser > maxAdviser:
							maxAdviser = adviser

					slot.scheduleAdviser(maxAdviser)
					competingAdvisers.remove(maxAdviser)
					time.sleep(self.debugDelay)


	def _readAdvisers(self):
		adviserPage = self._guiMngr.getPage('Advisers')
		
		names = adviserPage.read(col=0)[1:]
		endRow = names.index(None)
		if endRow < 0:
			return
		
		entries = adviserPage.getEntries(begin=(1, 0), end=(endRow, adviserPage.getEntryArray().numCols-1))
		entries.validate()
		
		for entryRow in entries:
			advData = [entry.get() for entry in entryRow]
			
			adviser = Adviser(advData)
			self._addAdviser(adviser)


	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def _createGUIPage(self):
		page = self._guiMngr.createPage('Schedule', EntryPage, {'numRows':0, 'numCols':0})
		
		timeBar = []
		for timeSlot in max(self._timeSlots, key=len):
			timeBar.append(timeSlot.getHour(mt=False))
		
		dayBar = []
		for dayRow in self._timeSlots:
			day = dayRow[0].getDay()
			dayBar.append([day])
		
		page.write([timeBar], begin=(0, 1))
		page.write(dayBar, begin=(1, 0))
		
		for dayIndex in range(len(self._timeSlots)):
			row = self._timeSlots[dayIndex]
			for colIndex in range(len(row)):
				slot = row[colIndex];	pos = (dayIndex+1, timeBar.index(slot.getHour(mt=False))+1)
				page.write(slot, pos=pos)
				
		
		page.getEntries(pos=(0, 0))._entries.state(['disabled'])
		for entry in page.getEntries(row=0):
			entry.state(['readonly'])
		for entry in page.getEntries(col=0):
			entry.state(['readonly'])

			
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def _addAdviser(self, adviser):
		for time in adviser.availability:
			for enumTimeRow in time.getEnumeratedTimes():
				dayIndex = self._dayOrder.index(enumTimeRow[0].getDay())
				dayRow = self._timeSlots[dayIndex]
				
				for enumTime in enumTimeRow:
					hrIndex = int((enumTime.getHour()-dayRow[0].getTime().getHour()) * self.timeSlotsPerHour)
					dayRow[hrIndex].addCompetingAdviser(adviser)
				
		self._advisers.append(adviser)