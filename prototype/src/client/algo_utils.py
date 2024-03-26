import math

class Processing_Unit:
    def __init__(self, macAddr, publishing_set, capacity):
        self._mac = macAddr
        self._freqs = publishing_set
        self._battery = capacity
    
    def changeInExecutions(self, newExecutions):
        return newExecutions - self._numExecutions
    
    def calculateExecutions(self):
        # only calculate number of executions if there is at least 1 item in _freqs

        # threshold for execution interval MAY CHANGE
        threshold = math.ceil(min(self._freqs) / 2) - 1



