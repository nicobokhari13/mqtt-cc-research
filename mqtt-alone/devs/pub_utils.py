import paho.mqtt.client as mqtt
from typing import Dict
import psutil
import subprocess
import random
import copy 

class PublisherUtils:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    # on Pi, grab mac address with terminal, not programmatically
    def __init__(self) -> None:
        # Other attributes/constants
        self._STATUS_TOPIC = "sensor/status" # where IoT device sends status
        self._got_cmd = None # set to true and mqtt awaits self. to be set to False after msg is received
        self._end_round = None # 
        self._publishes = {}
        self._current_executions = 0

    def setParameters(self,Mac_addr, start_battery, in_sim, energy_per_execution):
        # Set Attributes to Parameters
        #self._USERNAME = username
        #self._PASSWORD = password
        self._timeWindow = 60 # 1 minute = time window where dev sends status, waits for response on command 
        self._deviceMac = Mac_addr # mac address of IoT device 
        self._battery = float(start_battery)
        #self._CMD_TOPIC = "sensor/cmd/" + self._deviceMac # where IoT receives command on where to publish
        self._IN_SIM = in_sim
        self._ENERGY_PER_EXECUTION = float(energy_per_execution)

    def setPublishing(self, pub_cmd:dict):
        self._publishes = pub_cmd

    def decreaseSimEnergy(self):
        energyUsed = self._current_executions * self._ENERGY_PER_EXECUTION
        if self._battery != 0 and self._battery > energyUsed: 
            self._battery = self._battery - energyUsed
            return True
        else: 
            self._battery = 0
            return False
        
    def getExperimentEnergy(self):
        self._battery = psutil.sensors_battery().percent

    def saveNewExecutions(self, newExecutions):
        self._current_executions = float(newExecutions)
    
    def get_cpu_utilization(self):
        return psutil.cpu_percent(interval=5)
    
    def get_memory_utilization(self):
        return psutil.virtual_memory().percent
    
    def get_cpu_temperature(self):
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
        temperature = result.stdout.strip().split("=")[1]
        return temperature
    
    def randomizePublishes(self, topics, frequency_range):
        if frequency_range == 50:
            latency_min = 5
            latency_max = 55
        elif frequency_range == 40:
            latency_min = 10
            latency_max = 50
        elif frequency_range == 30:
            latency_min = 15
            latency_max = 45
        elif frequency_range == 20:
            latency_min = 20
            latency_max = 40
        elif frequency_range == 10:
            latency_min = 25
            latency_max = 35
    
        for i in range(len(topics)):
            random_latency = random.randint(latency_min, latency_max)
            self._publishes[topics[i]] = random_latency

    def getNumExecutions(self):
        numExecutions = 0
        # threshold for execution interval MAY CHANGE
        # example: 28 <-> 30 <-> 32
        threshold = 3
        # copy of freqs
        freqCopy = copy.deepcopy(list(self._publishes.values()))
        freq_min = min(freqCopy)
        # remove the min from the following calculations
        freqCopy.remove(freq_min)

        index = 1
        if freqCopy:
            # 
            for freq in freqCopy:
                multipleOfFreq = freq
                while multipleOfFreq <= 60:
                    if not((multipleOfFreq % freq_min < threshold) or ((freq_min - multipleOfFreq % freq_min) < threshold)):
                        numExecutions +=1
                    index += 1
                    multipleOfFreq = multipleOfFreq * index
        
        # the number of executions is the addition of all the times a frequency occurs in the OBSERVATION PERIOD
        numExecutions += 60 / freq_min
        self.saveNewExecutions(numExecutions)

    def getNumExecutions(self):
        #numExecutions = 0
        # threshold for execution interval MAY CHANGE
        # example: 28 <-> 30 <-> 32
        threshold = 3
        # copy of freqs
        freqCopy = copy.deepcopy(list(self._publishes.values()))

        if freqCopy: # if there are frequencies, then continue
            #freqCopy.remove(self._freq_min)
            print("don't remove min")
            pass
        else:# if you don't have any frequencies, then that means nothing is being added, so = 0 executions
            return 0
        # remove the min from the following calculations
        #freqCopy.remove(self._freq_min)
        frequency_multiples = ()
        same_execution_group = []
        group_min = None
        num_executions = 0 
        multiplier = 2

        if freqCopy:
            frequency_multiples = set(freqCopy)
            # check if there exists a number in the set of frequency_multiples where |multiplreOfFreq - freq| < threshold
            for freq in freqCopy: 
                multipleOfFreq = freq * multiplier
                while multipleOfFreq < 60:
                    frequency_multiples.add(multipleOfFreq)
                    multiplier+=1
                    multipleOfFreq = freq * multiplier
                multiplier = 2
            # convert the multiples back into a list for sorting in order
            print(frequency_multiples, type(frequency_multiples))
            frequency_multiples = list(frequency_multiples)
            frequency_multiples.sort()
            print(frequency_multiples, type(frequency_multiples))

            # after inserting all all multiples, loop through again, find a group of elements that are within threshold
            for i in range(len(frequency_multiples)):
                if i == 0: # if this is the first element
                    # then add it to the execution group 
                    same_execution_group.append(frequency_multiples[i])
                    group_min = frequency_multiples[i]
                    print("added the first element")
                else:
                    if abs(frequency_multiples[i] - group_min) < threshold:
                        # if the absolute value between the frequency multiple and group min is less than threshold
                        # then add it to the same execution group
                        same_execution_group.append(frequency_multiples[i])
                        # the group_min shouldn't change 
                        print("element in the same execution")
                    else:
                        # if this element is not within the group_min's threshold, then increase the number of executions, 
                        num_executions+=1
                        same_execution_group.clear()
                        same_execution_group.append(frequency_multiples[i])
                        group_min = frequency_multiples[i]
                        print("element not in the same execution, resetting group")
                        # reset the same_execution_group, and add the current element
                        # increment the number of executions
                        # reset group min
                print("num execution = ", num_executions)
                print('====')
                print("index = ", i)
                print("group = ", same_execution_group)
            
            if len(same_execution_group):
                num_executions+=1
            print("num executions = ", num_executions)

        self.saveNewExecutions(num_executions)

