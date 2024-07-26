from typing import Dict
from copy import deepcopy
from sim.container.topic import Topic_Container
import random

topic_c = Topic_Container()

class Devices:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        # possibly set some constants
        self._units: Dict[str, Processing_Unit] = dict()
        self._all_devices_energy_consumption = 0

    def setSensingEnergy(self, sense_energy):
        self.SENSING_ENERGY = sense_energy

    def setCommEnergy(self, comm_energy):
        self.COMMUNICATION_ENERGY = comm_energy

    def setThreshold(self, threshold):
        self.CONCURRENCY_THRESHOLD_MILISEC = threshold

    def setObservationPeriod(self, period):
        self.OBSERVATION_PERIOD_MILISEC = period

    # Called after completing a round for 1 algorithm
    # resets any parameters that may differ between algorithms
    def resetUnits(self):
        for device in self._units.values():
            device.resetAssignments()
            device._consumption = 0
            device._battery = 100
            device.setExecutions(new_value=0)
            device._sense_timestamp = []

    def clearUnits(self):
        self._units.clear()

    def clearAllDeviceEnergyConsumption(self):
        self._all_devices_energy_consumption = 0
        
    def calculateTotalEnergyConsumption(self):
        for device in self._units.values():
            executions = device.effectiveExecutions()
            device_energy_used = self.SENSING_ENERGY * len(device._sense_timestamp) + self.COMMUNICATION_ENERGY * executions
            self._all_devices_energy_consumption+=device_energy_used
            print("devicemac = ", device._device_mac)
            print("energy used = ", device_energy_used)
           # print("timestamps = ", device._sense_timestamp)
            print("device capability", device._capable_topics)
            print("num executions = ", executions)
            print("length of timestamps = ",len(device._sense_timestamp))
            print("--------")
class Processing_Unit:

    def __init__(self):
        self._assignments = {} # topic: publishing latency
        self._battery = 100 # p.allEnergyCapacity
        self._consumption = 0 # Ecurrent in the MQTTCC algo
        self._capable_topics = []
        self._num_executions_per_hour = 0
        # For calculating total energy consumption (for all algorithms)
        self._sense_timestamp = []

    def setMac(self, mac):
        self._device_mac = mac

    def addTimestamp(self, timestamp):
        self._sense_timestamp.append(timestamp)

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
        
    def setExecutions(self, new_value):
        self._num_executions_per_hour = new_value

    def updateConsumption(self, energy_increase):
        self._consumption+=energy_increase
        #print("consumption = ", self._consumption)

    # Performed to acquire device's total energy consumption from self._sense_timestamp
    # also used by MQTT-CC to calculate executions as tasks are added
    # def effectiveExecutions(self, new_task_timestamp = None):
    #     threshold = Devices._instance.CONCURRENCY_THRESHOLD_MILISEC
    #     # all the times in which the device must communicate, including those within the same execution group
    #     timestamp_set = list(self._sense_timestamp)
    #     if new_task_timestamp:
    #         timestamp_set.append(new_task_timestamp)
    #     if not timestamp_set:
    #         return 0
    #     timestamp_set = set(timestamp_set) # removes repeated timestamps (tasks that automatically communicate at the same time)
    #     timestamp_set = list(timestamp_set)
    #     timestamp_set.sort() # sort ascending order
    #     execution_group = []
    #     group_min = None
    #     num_executions = 0
    #     for i in range(len(timestamp_set)): # this finds if the timestamps occur within the same execution
    #         if i == 0:
    #             execution_group.append(timestamp_set[i])
    #             group_min = timestamp_set[i]
    #             #print("starting new execution")
    #         else:
    #             if abs(timestamp_set[i] - group_min) < threshold:
    #                 execution_group.append(timestamp_set[i])
    #             else:
    #                 num_executions+=1
    #                 execution_group.clear()
    #                 execution_group.append(timestamp_set[i])
    #                 group_min = timestamp_set[i]
    #                 #print("timestamp not in the same execution, resetting")
    #     if len(execution_group):
    #         num_executions+=1
    #     print(f"num execution = {num_executions}")

    #     return num_executions
    def effectiveExecutions(self, new_task_timestamp = None):
        threshold = Devices._instance.CONCURRENCY_THRESHOLD_MILISEC
        time_stamps = list(self._sense_timestamp)
        if new_task_timestamp:
            time_stamps.append(new_task_timestamp)
        if not time_stamps:
            return 0
        time_stamps.sort()
        last_execution_end = -threshold
        effective_executions = 0
        for time in time_stamps:
            if time >= last_execution_end + threshold:
                effective_executions+=1
                last_execution_end = time
        #print("executions = ", effective_executions)
        return effective_executions
    # # Performed for MQTT-CC only
    # def calculateExecutions(self, new_task_freq = None):
    #     threshold = Devices._instance.CONCURRENCY_THRESHOLD_MILISEC
    #     all_freqs = deepcopy(list(self._assignments.values()))
    #     if new_task_freq:
    #         all_freqs.append(new_task_freq)
    #     if not all_freqs:
    #         # if no frequencies, there are no executions
    #         return 0
    #     freq_multiples = set(all_freqs)
    #     execution_group = []
    #     group_min = None
    #     num_executions = 0
    #     multiplier = 1

    #     for freq in all_freqs:
    #         multiple = freq * multiplier
    #         while multiple < Devices._instance.OBSERVATION_PERIOD_MILISEC:
    #             freq_multiples.add(multiple)
    #             multiplier+=1
    #             multiple = freq * multiplier
    #         multiple = 1
    #     freq_multiples = list(freq_multiples) 
    #     freq_multiples.sort()
    #     for i in range(len(freq_multiples)):
    #         if i == 0:
    #             execution_group.append(freq_multiples[i])
    #             group_min = freq_multiples[i]
    #         else:
    #             if abs(freq_multiples[i] - group_min) < threshold:
    #                 execution_group.append(freq_multiples[i])
    #             else:
    #                 num_executions+=1
    #                 execution_group.clear()
    #                 execution_group.append(freq_multiples[i])
    #                 group_min = freq_multiples[i]
    #     if len(execution_group):
    #         num_executions+=1
    #     #print(f"device mac = {self._device_mac}")
    #     #print(f"num execution = {num_executions}")

    #     return num_executions

    # Performed by MQTT-EES and maxBattery 
    def energyIncrease(self, task_timestamp):
        newExecutions = self.effectiveExecutions(new_task_timestamp=task_timestamp)
        changeInExecutions = newExecutions - self._num_executions_per_hour
        # the change in the number of sensing events = 1
        # change in the number of communication events is the change in effective executions
        energyUsed = Devices._instance.SENSING_ENERGY + changeInExecutions * Devices._instance.COMMUNICATION_ENERGY
        return energyUsed

class Publisher_Container:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        # possibly set some constants
        self._devices = Devices()
        self._total_devices = 0
        pass
    # PERFORM THIS FUNCTION FIRST BEFORE ANYTHING ELSE
    def setDefaultNumPubs(self, default_num_pubs):
        self._default_num_pubs = default_num_pubs

    def setEnergies(self, sense_energy, comm_energy):
        self._devices.setSensingEnergy(sense_energy)
        self._devices.setCommEnergy(comm_energy)

    def setThreshold(self, threshold):
        self._devices.setThreshold(threshold)

    def setObservationPeriod(self, period):
        self._devices.setObservationPeriod(period)

    # Precondition: numPubs is a whole number > 0
    def generatePublisherMacs(self, numPubs):
        pub_macs = []
        for i in range(numPubs):
            name = f"dev00{i}"
            pub_macs.append(name)
        #print(pub_macs)
        return pub_macs

    def setupDevices(self, num_pubs):
        if num_pubs == 0:
            print(f"setting default devices {self._default_num_pubs}")
            num_pubs = self._default_num_pubs
        self._total_devices = num_pubs
        print(f"creating {num_pubs} devices")
        device_macs = self.generatePublisherMacs(num_pubs)
        for mac in device_macs:
            self._devices._units[mac] = Processing_Unit()
            self._devices._units[mac].setMac(mac)
        self.generateDeviceCapability()
    
    # Precondition: Topics are created 
    def generateDeviceCapability(self):
        found = False
        for unit in self._devices._units.values():
            num_capable_publishes = random.randint(a=2, b=topic_c._total_topics)
            # randomly sample this number of topics with their max_allowed_latency
            publishes = random.sample(population=topic_c._topic_dict.keys(), k=num_capable_publishes)
            unit.setCapableTopics(capability=publishes)
        for topic in topic_c._topic_dict.keys():
            for unit in self._devices._units.values():
                if unit.capableOfPublishing(topic):
                    found = True
                    break
            if not found:
                # if the topic is not covered by any device
                # get a random device
                rand_mac = random.choice(list(self._devices._units.keys()))
                # assign the topic t topicInCapable(self,)o it
                self._devices._units[rand_mac]._capable_topics.append(topic)
            # reset found to False
            found = False
        # all topic capabilities are created, saved, and cover all topics
            

        

            