from typing import Dict
from copy import deepcopy
from topic_container import Topic_Container
import random

class Devices:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        # possibly set some constants
        self._units: Dict[str, Processing_Unit] = dict()
        pass

class Processing_Unit:

    def __init__(self):
        self._assignments = {} # topic: publishing latency
        self._battery = 100
        self._consumption = 0
        self._capable_topics = []
        pass

    def setMac(self, mac):
        self._device_mac = mac

    def addAssignment(self, added_topic, added_qos):
        self._assignments[added_topic] = added_qos
    
    def resetAssignments(self):
        self._assignments.clear()    

    def setCapableTopics(self, capability:list):
        self._capable_topics = capability    

    def capableOfPublishing(self, topic):
        if topic in self._capable_topics:
            return True
        else:
            return False

class Publisher_Container:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        # possibly set some constants
        self._default_num_pubs = 8
        pass

    def generatePublisherMacs(numPubs):
        pub_macs = []
        for i in range(numPubs):
            name = f"dev00{i}"
            pub_macs.append(name)
        print(pub_macs)
        return pub_macs

    def generateDevices(self, num_pubs):
        if num_pubs == 0:
            print(f"setting default devices {self._default_num_pubs}")
            num_pubs = self._default_num_pubs
        print(f"creating {num_pubs} devices")
        devices = Devices()
        device_macs = self.generatePublisherMacs(num_pubs)
        for mac in device_macs:
            devices._units[mac] = Processing_Unit()
            devices._units[mac].setMac(mac)

    def generateDeviceCapability(self):
        found = False
        devices = Devices()
        topics = Topic_Container()
        for unit in devices._units.values():
            num_capable_publishes = random.randrange(start=1, stop=topics._total_topics + 1)
            # randomly sample this number of topics with their max_allowed_latency
            publishes = random.sample(population=topics._topic_dict.keys(), k=num_capable_publishes)
            unit.setCapableTopics(capability=publishes)
        for topic in topics._topic_dict.keys():
            for unit in devices._units.values():
                if unit.capableOfPublishing(topic):
                    found = True
                    break
            if not found:
                # if the topic is not covered by any device
                # get a random device
                rand_mac = random.choice(devices._units.keys())
                # assign the topic t topicInCapable(self,)o it
                devices._units[rand_mac]._capable_topics.append(topic)
            # reset found to False
            found = False
            

        

            