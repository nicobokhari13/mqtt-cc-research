import time
import paho.mqtt.client as mqtt
import json
from typing import Dict

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
        self._publishes = None
        self._current_executions = 0
        

    def setParameters(self, username, password, Mac_addr, start_battery, in_sim, energy_per_execution):
        # Set Attributes to Parameters
        self._USERNAME = username
        self._PASSWORD = password
        self._timeWindow = 60 # time window where dev sends status, waits for response on command
        self._deviceMac = Mac_addr # mac address of IoT device 
        self._battery = float(start_battery)
        self._CMD_TOPIC = "sensor/cmd/" + self._deviceMac # where IoT receives command on where to publish
        self._IN_SIM = in_sim
        self._ENERGY_PER_EXECUTION = energy_per_execution

    def setPublishing(self, pub_cmd:dict):
        self._publishes = pub_cmd

    def decreaseSimEnergy(self):
        energyUsed = self._current_executions * self._ENERGY_PER_EXECUTION
        if self._battery > 0 and self._battery > energyUsed: 
            self._battery = self._battery - energyUsed
            return True
        else: 
            self._battery = 0
            return False

    def saveNewExecutions(self, newExecutions):
        self._current_executions = newExecutions