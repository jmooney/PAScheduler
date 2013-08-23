'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - TimeSlot
	
	Description:
		Maintains data specific to one scheduleable slot. Provides methods for updating/changing scheduled advisers.
		
'''

# Imports


#------------------------------------------------------------------#

class TimeSlot(object):
	
	def __init__(self, time, density):
		super().__init__()
		
		self._time = time
		self._density = density

		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def getDay(self):
		return self._time.format(day=True)
	def getHour(self, mt=True):
		return self._time.format(hour=True, time='Standard')
		
		
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	
	def __str__(self):
		return str(self._time) + ' ' + str(self._density)
