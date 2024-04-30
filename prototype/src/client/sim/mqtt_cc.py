from pub_container import Publisher_Container
from topic_container import Topic_Container
from subscriber_container import Subscriber_Container

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

    def mqttcc_algo(self):
        pass
    