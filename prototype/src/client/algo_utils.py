import math
from typing import Dict
class Processing_Unit:
    _OBSERVATION_PERIOD = 60
    _ENERGY_PER_EXECUTION = 10

    def __init__(self, macAddr:str, capacity:float, executions):
        self._mac = macAddr
        self._freqs = {}
        self._battery = capacity
        self._numExecutions = executions 
        self._assignments = {}

    def currentEnergy(self):
        return self._numExecutions * Processing_Unit._ENERGY_PER_EXECUTION

    def resetMinimum(self):
        if self._freqs:
            self._freq_min = min(self._freqs)
        else:
            self._freq_min = None

    def setFrequencies(self, publishing_list):
        self._freqs = set(publishing_list)
        self._freqs = list(self._freqs)
        self.resetMinimum()
    
    def calculateExecutions(self, newTask = None):
        numExecutions = 0
        # threshold for execution interval MAY CHANGE
        # example: 28 <-> 30 <-> 32
        threshold = 3
        # list that will hold removals
        removes = list()
        # copy of freqs
        freqCopy = self._freqs

        # if there is a newTask, add it to the copy to simulate adding the task to the publisher
        if newTask: 
            # if there is a new task, add it to freqs, change the min
            freqCopy.append(newTask)
            self._freq_min = min(freqCopy)

        # remove the min from the following calculations
        freqCopy.remove(self._freq_min)

        # if freqCopy has any items other than the minimum just removed,

        if freqCopy:
            # Remove the ones that are within a threshold of a multiple of the minimum frequency
            removes = [freq for freq in freqCopy if (freq % self._freq_min < threshold) or ((self._freq_min - freq % self._freq_min) < threshold)]
            # Remove the numbers from freqCopy
            freqCopy = [freq for freq in freqCopy if freqCopy not in removes]
        
        # place minimum back in
        freqCopy.append(self._freq_min)
        for freq in freqCopy:
            numExecutions += math.ceil(self._OBSERVATION_PERIOD / freq)

        # reset self._freqs_min to actual min if the min was changed for the newTask
        if newTask:
            self.resetMinimum()

        return numExecutions
    
    def resetExecutions(self):
        self._numExecutions = self.calculateExecutions()
    
    def energyIncrease(self, task):
        newExecutions = self.calculateExecutions(newTask = task)
        changeInExecutions = newExecutions - self._numExecutions
        return changeInExecutions * self._ENERGY_PER_EXECUTION
    
    def addAssignment(self, topic:str, task):
        self._assignments[topic] = task
        # add topic's frequency to device frequencies
        self._freqs.append(task)
        # example: 
        # "sensor/temperature": 10 -> publish to sensor/temperature every 10 seconds

    def addPublishings(self, publishing_set:list):
        # publishing_set is a list of tuples (topic, max_allowed_latency)
        for publishing in publishing_set:
            print(publishing)
            self.addAssignment(topic = publishing[0], task = publishing[1])
        # after all frequencies added, reset frequency minimum 
        self.resetMinimum()
                

class Devices:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        # key = macAddr, value = Processing_Unit
        self._units: Dict[str, Processing_Unit] = dict()
        self._generated_cmd: Dict[str, str] = dict()

    def addProcessingUnit(self, newUnit:Processing_Unit):
        self._units[newUnit._mac] = newUnit

    def resetUnits(self):
        self._units.clear()

    def addAssignmentsToCommand(self, deviceMac:str, taskList:str):
        self._generated_cmd[deviceMac] = taskList
        # example
        # b8:27:eb:4f:15:95 : "{"sensor/temperature":10, "sensor/airquality": 34}""

    

    

        





