import math

class Processing_Unit:
    def __init__(self, macAddr:str, publishing_set:list, capacity:float, executions):
        self._mac = macAddr
        self._freqs = publishing_set
        self._battery = capacity
        self._freq_min = min(self._freqs)
        self._numExecutions = executions 
        self._OBSERVATION_PERIOD = 60
        self._ENERGY_PER_EXECUTION = 10
    
    def calculateExecutions(self, newTask = None):
        if newTask: 
            # if there is a new task, add it to freqs, change the min if necessary
            self._freqs.append(newTask)
            self._freq_min = min(self._freqs)
        numExecutions = 0
        # threshold for execution interval MAY CHANGE
        threshold = math.ceil(self._freq_min / 2) - 1
        # list that will hold removals
        removes = list()
        # copy of freqs
        freqCopy = self._freqs
        # remove the min for these calculations
        freqCopy.remove(self._freq_min)
        # Remove the numbers that are within a threshold of a multiple of the minimum frequency
        removes = [freq for freq in freqCopy if (freq % self._freq_min < threshold) or ((self._freq_min - freq % self._freq_min) < threshold)]
        # Remove the numbers from freqCopy
        freqCopy = [freq for freq in freqCopy if freqCopy not in removes]
        # place minimum back in
        freqCopy.append(self._freq_min)
        for i in range(len(freqCopy)):
            numExecutions += math.ceil(self._OBSERVATION_PERIOD / freqCopy[i])
        return numExecutions
                

class Devices:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        # key = macAddr, value = Processing_Unit
        self._units = dict()

    def addProcessingUnit(self, newUnit:Processing_Unit):
        newUnit._numExecutions = newUnit.calculateExecutions()
        self._units[newUnit._mac] = newUnit

    def resetUnits(self):
        self._units.clear()
    

    

        





