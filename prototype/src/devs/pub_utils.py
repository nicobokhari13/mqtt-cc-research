# Utilities for the publishing devices 
    # store and retrieve important information
import time
import paho.mqtt.client as mqtt
import json

class PublisherUtils:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    # on Pi, grab mac address with terminal, not programmatically
    def __init__(self, ) -> None:
        # Other attributes/constants
        self._STATUS_TOPIC = "sensor/status" # where IoT device sends status
        self._CMD_TOPIC = "sensor/cmd" # where IoT receives command on where to publish
        self._got_cmd = None # set to true and mqtt awaits self. to be set to False after msg is received
        self._end_round = None # 

    def setParameters(self, username, password, pub_topics, sample_frequency, Mac_addr, start_battery):
        # Set Attributes to Parameters
        self._USERNAME = username
        self._PASSWORD = password
        self._pubtopics = pub_topics # all topics dev is capable of publishing to
        self._timeWindow = 30 # time window where dev sends status, waits for response on command
        self._MAC_ADDR = Mac_addr # mac address of IoT device 
        self._SAMPLE_FREQ = sample_frequency # fixed sample_freq of IoT device
        self._battery = start_battery