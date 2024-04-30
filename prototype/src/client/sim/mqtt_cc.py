from pub_container import Publisher_Container
from topic_container import Topic_Container
from subscriber_container import Subscriber_Container
from copy import deepcopy

# to access the singleton instance easily
pub_c = Publisher_Container()
sub_c = Subscriber_Container()
topic_c = Topic_Container()

class MQTTCC:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._algo_name = "cc"
        self._total_energy_consumption = 0
    
    def resetEnergyConsumption(self):
        self._total_energy_consumption = 0
        pass

    # system capability used to track which publishers can publish to
    def copyOfSystemCapability(self, capability):
        self._system_publishing = deepcopy(capability)

    # timeline used to calculate total energy consumption
    def copyOfTopicTimeStamps(self):
        self._experiment_timeline = deepcopy(topic_c._all_sense_timestamps)
    
    def mqttcc_algo(self):
        # for each topic in topic_dict
            # get tuple from system publishing 
                # for each device mac in the topic capability
                    # perform the energyIncrease() function per device
                    # get best mac
                # if bestmac
                    # assign task to mac with addAssignment
        # calculate total energy consumption
        pass
    