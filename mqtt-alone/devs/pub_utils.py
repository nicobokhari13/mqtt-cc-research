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

