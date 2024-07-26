from container.publisher import Publisher_Container
from container.topic import Topic_Container
from container.subscriber import Subscriber_Container
from copy import deepcopy
import random 
from constants import ConfigUtils


# to access the singleton instance easily
pub_c = Publisher_Container()
sub_c = Subscriber_Container()
topic_c = Topic_Container()

class Standard:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._algo_name = "mqtt_algo"
        self._total_energy_consumption = 0
        pass

    def copyOfSystemCapability(self, capability):
        # a dictionary with each topic's capable devices for publishing to t
        self._system_capability = deepcopy(capability)

    def copyOfTopicTimeStamps(self):
        # a dictionary with each topic's sense execution timestamp < T observation period
            # topic/1: [10,20,30...]
        self._experiment_timeline = deepcopy(topic_c._all_sense_timestamps)

    def saveDevicesTotalEnergyConsumed(self, random_energy_consumption):
        self._total_energy_consumption+= random_energy_consumption

    def resetTotalConsumption(self):
        self._total_energy_consumption = 0
        
    def findNextTask(self):
        fmin = -1
        tmin = None
        for topic in topic_c._topic_dict.keys():
            # get the first timestamp for that topic
            if topic in self._experiment_timeline.keys():
                fi = self._experiment_timeline[topic][0] 
            # if its min, set it as min
                if (fmin < 0) or (fi < fmin):
                    tmin = topic
                    fmin = fi
        # at this point fmin holds the next timestamp, and tmin holds which topic to publish to
        # remove the timestamp from the topic's list
        if tmin:
            self._experiment_timeline[tmin].pop(0)

        if not self._experiment_timeline[tmin]:
            print("topic list", tmin, self._experiment_timeline[tmin])
            # if the list at this key is empty, remove the key
            del self._experiment_timeline[tmin]
        
        return [tmin, fmin]
        # fmin = -1
        # tmin = None
        # for each topic in topic dict keys
            # if fmin < 0 or fi < fmin
                # tmin = ti
                # fmin = fi
        # pop fi from ti's timestamp list
        # if ti's timestamp list is empty, remove ti from the keys
        # return [ti, fi]

    def random_algo(self):
            while len(self._experiment_timeline.keys()) > 0:
                #print("=============")
                #print(self._system_capability)
                [newTask, newTaskTimeStamp] = self.findNextTask()
                #print([newTask, newTaskTimeStamp])
                # if the index of the publishing device is -1, or the index is at the end of the list
                #print("index = ", self._system_capability[newTask][0])

                # get a random index in system_capability[topic][1]
                random_index = random.randrange(start=0, stop=len(self._system_capability[newTask][1]))
                self._system_capability[newTask][0] = random_index
                publishing_mac = self._system_capability[newTask][1][random_index]            
                pub_c._devices._units[publishing_mac].addTimestamp(timestamp=newTaskTimeStamp)

            print("done with random algo")

    def mqtt_algo(self):
        config = ConfigUtils._instance
        endAlgo = False
        while len(self._experiment_timeline.keys()) > 0:
            [newTask, newTaskTimeStamp] = self.findNextTask()
            print("time = ", newTaskTimeStamp)
            for deviceMac in self._system_capability[newTask][1]:
                energyIncrease = pub_c._devices._units[deviceMac].energyIncrease(task_timestamp=newTaskTimeStamp)
                if energyIncrease + pub_c._devices._units[deviceMac]._consumption >= pub_c._devices._units[deviceMac]._battery:
                    endAlgo = True
                else:
                    pub_c._devices._units[deviceMac].updateConsumption(energyIncrease)
                    pub_c._devices._units[deviceMac].addTimestamp(timestamp=newTaskTimeStamp)
                    pub_c._devices._units[deviceMac].setExecutions(new_value=pub_c._devices._units[deviceMac].effectiveExecutions())
                if endAlgo:
                    print("leaving standard mqtt algo")
                    break
            if endAlgo:
                print("leaving standard mqtt algo")
                return newTaskTimeStamp
        print("done with standard algo")
        return None
                  
