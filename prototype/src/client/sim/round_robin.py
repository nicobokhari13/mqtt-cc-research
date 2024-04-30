from pub_container import Publisher_Container
from topic_container import Topic_Container
from subscriber_container import Subscriber_Container
from copy import deepcopy

# to access the singleton instance easily
pub_c = Publisher_Container()
sub_c = Subscriber_Container()
topic_c = Topic_Container()

class RR:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._algo_name = "rr"
        self._total_energy_consumption = 0
        pass

    def copyOfSystemCapability(self, capability):
        self._system_publishing = deepcopy(capability)

    def copyOfTopicTimeStamps(self):
        self._experiment_timeline = deepcopy(topic_c._all_sense_timestamps)

    def findNextTask(self):
        # fmin = -1
        # tmin = None
        # for each topic in topic dict keys
            # if fmin < 0 or fi < fmin
                # tmin = ti
                # fmin = fi
        # pop fi from ti's timestamp list
        # if ti's timestamp list is empty, remove ti from the keys
        # return [ti, fi]
        pass

    def rr_algo(self):
        # while len(timeline.keys()) > 0
            # [newTask, newTaskTimeStamp] = findNextTask()
            # get tuple for topic = newTask in system capability
                # if tuple[0] = None or tuple[0] + 1 > len(tuple[1]), set to 0
                # else, tuple[0]+=1
                # get mac from list tuple[1] at index tuple[0]
                # add timestamp to device
        # calculate total energy consumption
        pass

