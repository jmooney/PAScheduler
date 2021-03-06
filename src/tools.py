
'''

	Author:	John Mooney
	Date:		08/05/2013
	
	PAScheduler 2 - tools
	
	Description:
		Various useful functions
		
'''

def frange(x, y, step):
	while x < y:
		yield x
		x += step
		
		
def dictionaryToOrderedList(dict, keyOrder):
	newList = []
	for k in keyOrder:
		try:
			newList.append(dict[k])
		except KeyError:
			continue
			
	return newList
	
	
def pos(num):
	return num if num > 0 else 0
	
def getAverage(nums):
	return sum(nums)/len(nums)
	