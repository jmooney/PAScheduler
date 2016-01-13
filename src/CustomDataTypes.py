
'''

    Author: John Mooney
    Date:   1/12/2016
    
    PAScheduler 2 - CustomDataTypes
    
    Description:
        Provides custom types for TypedEntry classes.
        
'''

import re


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
        raise ValueError('Invalid Input for ' + str(self.__class__) + ' Object')


#---------------------------------------------------------------#

class RestrictedStr(InputObject):

    _availChars = '.'
    _maxLength = '*'
    grammarDescriptor = '^.*$'


    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    @classmethod
    def make(cls, availChars, maxLength):
        newMaxLength = '*'
        if (maxLength):
            newMaxLength = '{1,'+str(maxLength) + '}'

        return type("RestrictedStrClassObj", (cls,), dict(\
            _maxLength = newMaxLength, _availChars = availChars, \
            grammarDescriptor = '^({}){}$'.format(availChars, newMaxLength)))

    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    def asBool(self):
        return self._data.upper() == 'R'


    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def __init__(self, data):
        super().__init__(data)
        self._data = data
    def __str__(self):
        return self._data
    __repr__ = __str__
