from pub_container import Publisher_Container
from topic_container import Topic_Container
from subscriber_container import Subscriber_Container
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

    def mqtt_algo(self):
        config = ConfigUtils._instance
        endAlgo = False
        # while there are sensing tasks on the timeline
        while len(self._experiment_timeline.keys()) > 0:
            # get the next topic to be published to, and the timestamp
            [newTask, newTaskTimeStamp] = self.findNextTask()
            print("time = ", newTaskTimeStamp)
            for deviceMac in self._system_capability[newTask][1]:
                # for each device capable of performing the sensing_task
                # model the energy increase resulting from adding the task to the device
                energyIncrease = pub_c._devices._units[deviceMac].energyIncrease(task_timestamp=newTaskTimeStamp)

                if energyIncrease + pub_c._devices._units[deviceMac]._consumption >= pub_c._devices._units[deviceMac]._battery:
                    # if energy increase goes above device battery, 
                    # end algorithm
                    endAlgo = True
                else:
                    # subtract energy consumption from device's battery
                    pub_c._devices._units[deviceMac].updateConsumption(energyIncrease)
                    # add the timestamp the device performs the sensing task
                    pub_c._devices._units[deviceMac].addTimestamp(timestamp=newTaskTimeStamp)
                    # re-calculate the number of effective executions the device now performs
                    pub_c._devices._units[deviceMac].setExecutions(new_value=pub_c._devices._units[deviceMac].effectiveExecutions())
                if endAlgo:
                    print("leaving standard mqtt algo")
                    break
            if endAlgo:
                print("leaving standard mqtt algo")
                return newTaskTimeStamp
        print("done with standard algo")
        return None
                  
