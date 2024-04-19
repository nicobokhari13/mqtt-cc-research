import math
from typing import Dict
import copy
class Processing_Unit:
    _OBSERVATION_PERIOD = 60
    # same as publisher simulation start scripts (run_devXX.sh) 

    def __init__(self, macAddr:str, capacity:float, executions):
        self._mac = macAddr
        self._freqs = list()
        self._battery = capacity
        self._numExecutions = executions 
        self._assignments = {}
        self._freq_min = None

    def currentEnergy(self):
        return self._numExecutions * Devices._instance._ENERGY_PER_EXECUTION

    def resetMinimum(self):
        if self._freqs:
            self._freq_min = min(self._freqs)
        else:
            self._freq_min = None
    
    def calculateExecutions(self, newTask = None):
        numExecutions = 0
        # threshold for execution interval MAY CHANGE
        # example: 28 <-> 30 <-> 32
        threshold = Devices._instance._CONCURRENCY_THRESHOLD
        # list that will hold removals
        removes = list()
        # copy of freqs
        freqCopy = copy.deepcopy(self._freqs)

        # if there is a newTask, add it to the copy to simulate adding the task to the publisher
        if newTask:  
            # if there is a new task, add it to freqs, change the min
            freqCopy.append(newTask)
            self._freq_min = min(freqCopy)
        if self._freq_min:
            freqCopy.remove(self._freq_min)
        else:# if you don't have a minimum, then the list is empty, no executions -> 
            return 0
        # remove the min from the following calculations
        #freqCopy.remove(self._freq_min)

        # if freqCopy has any items other than the minimum just removed,
        index = 1
        if freqCopy:
            # 
            for freq in freqCopy:
                multipleOfFreq = freq
                while multipleOfFreq <= self._OBSERVATION_PERIOD:
                    if not((multipleOfFreq % self._freq_min < threshold) or ((self._freq_min - multipleOfFreq % self._freq_min) < threshold)):
                        numExecutions +=1
                    index += 1
                    multipleOfFreq = multipleOfFreq * index
                        
        # place minimum back in
        freqCopy.append(self._freq_min)
        
        # the number of executions is the addition of all the times a frequency occurs in the OBSERVATION PERIOD
        numExecutions += self._OBSERVATION_PERIOD / self._freq_min

        # reset self._freqs_min to actual min if the min was changed for the newTask
        if newTask:
            self.resetMinimum()

        return numExecutions
    
    def resetExecutions(self):
        self._numExecutions = self.calculateExecutions()
    
    def energyIncrease(self, task):
        newExecutions = self.calculateExecutions(newTask = task)
        changeInExecutions = newExecutions - self._numExecutions
        print(f"change in executions: {changeInExecutions}")
        return changeInExecutions * Devices._instance._ENERGY_PER_EXECUTION
    
    def addAssignment(self, topic:str, task, isNew = None):
        self._assignments[topic] = task
        self._freqs.append(task)
        self.resetMinimum()
        # add assignment to publisher
        print(self._assignments)
        # example: 
        # "sensor/temperature": 10 -> publish to sensor/temperature every 10 seconds

    def addPublishings(self, publishing_list:list):
        # publishing_set is a list of tuples (topic, max_allowed_latency)
        for publishing in publishing_list:
            print(publishing)
            self.addAssignment(topic = publishing[0], task = publishing[1])
            # add topic's frequency to device frequencies
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
    
    def addEnergyPerExecution(self, energy):
        self._ENERGY_PER_EXECUTION = float(energy)

    def addConcurrencyThreshold(self, threshold):
        self._CONCURRENCY_THRESHOLD = int(threshold)
        

    def addAssignmentsToCommand(self, deviceMac:str, taskList:str):
        self._generated_cmd[deviceMac] = taskList
        # example
        # b8:27:eb:4f:15:95 : "{"sensor/temperature":10, "sensor/airquality": 34}""

    

    

        





