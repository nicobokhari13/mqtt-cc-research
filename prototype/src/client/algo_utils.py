import math
from typing import Dict
class Processing_Unit:
    def __init__(self, macAddr:str, capacity:float, executions):
        self._mac = macAddr
        self._freqs = ()
        self._battery = capacity
        self._freq_min = min(self._freqs)
        self._numExecutions = executions 
        self._OBSERVATION_PERIOD = 60
        self._ENERGY_PER_EXECUTION = 10
        self._assignments = {}
        # TODO: use json.dumps to turn assignments dictionary into json string

    def setFrequencies(self, publishing_list):
        self._freqs = set(publishing_list)
        self.resetMinimum()
    
    def currentEnergy(self):
        return self._numExecutions * self._ENERGY_PER_EXECUTION

    def resetMinimum(self):
        self._freq_min = min(self._freqs)
    
    def calculateExecutions(self, newTask = None):
        numExecutions = 0
        # threshold for execution interval MAY CHANGE
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

        # reset self._freqs_min to actual min if the min was changed for the newTask
        if newTask:
            self.resetMinimum()

        return numExecutions
    
    def energyIncrease(self, task):
        newExecutions = self.calculateExecutions(newTask = task)
        changeInExecutions = newExecutions - self._numExecutions
        return changeInExecutions * self._ENERGY_PER_EXECUTION
    
    def addPublishings(self, publishing_set:list):
        # publishing_set is a list of tuples (topic, max_allowed_latency)
        frequencies = list()
        for publishing in publishing_set:
            self.addAssignment(topic = publishing[0], task = publishing[1])
            frequencies.append(publishing[1])
        self.setFrequencies(frequencies)


    def addAssignment(self, topic:str, task):
        self._assignments[topic] = task
        self._freqs.add(task)
        self.resetMinimum()
        # example: 
        # "sensor/temperature": 10 -> publish to sensor/temperature every 10 seconds

                

class Devices:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        # key = macAddr, value = Processing_Unit
        self._units: Dict[str, Processing_Unit]
        self._generated_cmd: Dict[str, str]

    def addProcessingUnit(self, newUnit:Processing_Unit):
        self._units[newUnit._mac] = newUnit

    def resetUnits(self):
        self._units.clear()

    def addAssignmentsToCommand(self, deviceMac:str, taskList:str):
        self._generated_cmd[deviceMac] = taskList
        # example
        # b8:27:eb:4f:15:95 : "{"sensor/temperature":10, "sensor/airquality": 34}""


    

    

        





