from container.publisher import Publisher_Container
from container.topic import Topic_Container
from container.subscriber import Subscriber_Container
from copy import deepcopy
from constants import ConfigUtils

#------------------------------------------#


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
    
    def saveDevicesTotalEnergyConsumed(self, cc_energy_consumption):
        self._total_energy_consumption+= cc_energy_consumption
    
    # system capability used to track which publishers can publish to
    def copyOfSystemCapability(self, capability:dict):
        self._system_capability = deepcopy(capability)

    # timeline used to calculate total energy consumption
    def copyOfTopicTimeStamps(self):
        self._experiment_timeline = deepcopy(topic_c._all_sense_timestamps)
        
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

    def mqttcc_algo(self):
        config = ConfigUtils._instance
        # add "end algorithm" boolean 
        endAlgo = False
        while len(self._experiment_timeline.keys()) > 0:
            [newTask, newTaskTimeStamp] = self.findNextTask()
            print("topic ", newTask, " time ", newTaskTimeStamp)
            Emin = -1
            Einc = None
            EincMin = None
            Enew = None
            Eratio = None
            bestMac = None
            for deviceMac in self._system_capability[newTask][1]:
                #print("\t devicemac = ", deviceMac)
                # for each device capable of publishing to newTask
                # calculate energy increase from adding the new task
                Einc = pub_c._devices._units[deviceMac].energyIncrease(newTaskTimeStamp)
                Enew = pub_c._devices._units[deviceMac]._consumption + Einc
                Eratio = Enew / pub_c._devices._units[deviceMac]._battery
                if (Emin < 0) or (Enew <= pub_c._devices._units[deviceMac]._battery and Eratio < Emin):
                    bestMac = deviceMac
                    Emin = Eratio 
                    EincMin = Einc
                if (Enew >= pub_c._devices._units[deviceMac]._battery):
                    #print("device reduced to 0 for observation periods >= ", constants.ConfigUtils._instance.OBSERVATION_PERIOD_MILISEC)
                    print("last time = ",newTaskTimeStamp)
                    endAlgo = True
                    # exit algorithm
                if endAlgo:
                    break
            if endAlgo:
                print("leaving mqtt_cc algo")
                return newTaskTimeStamp
            if bestMac:
                # After each allocation
                    # update the consumption
                    # add the timestmap
                    # update the number of executions since efficient energy index depends on executions
                # if the device is the best for the new task
                # assign it to the device
                #print("best mac = ", bestMac)
                #print("device increase = ", EincMin)
                #pub_c._devices._units[bestMac].addAssignment(added_topic=newTask, added_qos=topic_c._topic_dict[newTask])
                # add the consumption estimate from mqttcc algo
                pub_c._devices._units[bestMac].updateConsumption(EincMin)
                # update number of executions
                pub_c._devices._units[bestMac].addTimestamp(timestamp=newTaskTimeStamp)
                bestMac_new_executions = pub_c._devices._units[bestMac].effectiveExecutions()
                pub_c._devices._units[bestMac].setExecutions(new_value=bestMac_new_executions)
                # add the task's timestamp to the device
                #print("========")
        return None