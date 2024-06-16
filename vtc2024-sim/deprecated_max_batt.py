# D
from pub_container import Publisher_Container
from topic_container import Topic_Container
from subscriber_container import Subscriber_Container
from copy import deepcopy

# to access the singleton instance easily
pub_c = Publisher_Container()
sub_c = Subscriber_Container()
topic_c = Topic_Container()

class MB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._algo_name = "MB"
        self._total_energy_consumption = 0
        pass

    def copyOfSystemCapability(self, capability):
        # a dictionary with each topic's capable devices for publishing to 
        # key = topic, value = list of deviceMacs
        self._system_capability = deepcopy(capability)

    def copyOfTopicTimeStamps(self):
        # a dictionary with each topic's sense execution timestamp < T observation period
            # topic/1: [10,20,30...]
        self._experiment_timeline = deepcopy(topic_c._all_sense_timestamps)
        
    def saveDevicesTotalEnergyConsumed(self, MB_energy_consumption):
        # total energy consumption = system's overall energy consumption
        # where MB_energy_consumption is the energy consumed by a device
        # which was allocated a sensing task because it had the maximum battery
        # of all devices in the system at the time of allocation
        self._total_energy_consumption += MB_energy_consumption

    def resetTotalConsumption(self):
        self._total_energy_consumption = 0
        
    def findNextTask(self):
        fmin = -1 # minimum timestamp occuring in the future
        tmin = None # topic published to at fmin timestamp
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

    def rr_algo(self):
            while len(self._experiment_timeline.keys()) > 0:
                [newTask, newTaskTimeStamp] = self.findNextTask()
                # if the index of the publishing device is -1, or the index is at the end of the list
                if (self._system_capability[newTask][0] < 0) or (self._system_capability[newTask][0] + 1 >= len(self._system_capability[newTask][1])):
                    # set the index to the first publisher
                    self._system_capability[newTask][0] = 0
                else:
                    self._system_capability[newTask][0]+= 1
                publishing_mac = self._system_capability[newTask][1][self._system_capability[newTask][0]]
                pub_c._devices._units[publishing_mac].addTimestamp(timestamp=newTaskTimeStamp)
            # by this point, all timestamps have been allocated to devices according to RR
            print("done with rr algo")

    def max_batt_algo(self):
        # while there are still sensing tasks in the experiemnt timeline, 
        while len(self._experiment_timeline.keys()) > 0:
            # get the next sensing task and the time to perform task
            [newTask, newTaskTimeStamp] = self.findNextTask()
            # set bestMac as the first element
            bestMac = self._system_capability[newTask][1][0]
            maxBattery = pub_c._devices._units[bestMac]._battery - pub_c._devices._units[bestMac]._consumption
            for deviceMac in self._system_capability[newTask][1]:
                macRemainingBattery = pub_c._devices._units[deviceMac]._battery - pub_c._devices._units[deviceMac]._consumption
                if maxBattery < macRemainingBattery:
                    bestMac = deviceMac
                    maxBattery = macRemainingBattery
            # bestMac should have the mac of the device with the maximum remaining battery

            # update consumption with energy increase from adding timestamp
            energy_consumed = pub_c._devices._units[bestMac].energyIncrease(task_timestamp=newTaskTimeStamp)
            pub_c._devices._units[bestMac].updateConsumption(energy_increase=energy_consumed)
            #add timestamp 
            pub_c._devices._units[bestMac].addTimestamp(timestamp=newTaskTimeStamp)

            # update number of executions since energyIncrease depends on change in executions
            bestMac_new_executions = pub_c._devices._units[bestMac].effectiveExecutions()
            pub_c._devices._units[bestMac].setExecutions(new_value=bestMac_new_executions)
        print("done with max_batt_algo")
            # set bestMac = first device in system capability of newTask
            # maxBattery = bestMac.battery - bestMac.consumption
            # loop through all macs in system capability of new Task
                # if maxBattery < (mac.battery - mac.consumption):
                    # bestMac = mac
                    # maxBattery = mac.battery - mac.consumption
            # pub_c.devices[bestMac].addtimestamp(newTaskTimestamp)
            
        # publishing mac is one where the publisher's capacity - consumption is maximum