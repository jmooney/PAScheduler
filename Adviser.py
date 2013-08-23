'''

	Author:	John Mooney
	Date:		07/16/2013
	
	PAScheduler 2 - Adviser
	
	Description:
		Maintains adviser-specific data and methods in scheduling.
		
'''


# Imports



#------------------------------------------------------------------#

class Adviser(object):

	def __init__(self, data):
		super().__init__()
		
		self.name 		= data[0]
		self.major 		= data[1]
		self.year 		= data[2]
		self.minHrs 	= data[3]
		self.reqtdHrs 	= data[4]
		self.maxHrs 	= data[5]
		self.availability = data[6]

	
	''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
	