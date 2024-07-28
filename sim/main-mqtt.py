from constants import ConfigUtils
from datetime import datetime
from container.publisher import Publisher_Container
from container.topic import Topic_Container
from container.subscriber import Subscriber_Container
import random
import sys
import csv
from schedulers.mqtt_cc import MQTTCC
# from schedulers.round_robin import RR
# from schedulers.max_batt import MB
# from schedulers.min_task import MT
from schedulers.random_algo import Random
from schedulers.mqtt_algo import Standard

#------------------------------------------#


### GLOBAL CONSTANTS
config_file = sys.argv[1]
last_msg = sys.argv[2]
# EXPERIMENT SET UP
configuration = ConfigUtils()
configuration.setConstants(configFilePath=config_file)
file_paths = {
    "pub_path": "results_pubs/",
    "sub_path": "results_subs/",
    "topic_path": "results_topics/",
    "threshold_path": "results_thresh/"
}
filename = "results_" + str(datetime.now()) + "_"

# create containers
pub_c = Publisher_Container()
sub_c = Subscriber_Container()
topic_c = Topic_Container()

# Set Defaults
pub_c.setDefaultNumPubs(configuration._default_num_pubs)
sub_c.setDefaultNumSubs(configuration._default_num_subs)
topic_c.setDefaultNumTopics(configuration._default_num_topics)

# other constants
sub_c.setLatencyMinMax(min=configuration._LAT_QOS_MIN, max=configuration._LAT_QOS_MAX)
pub_c.setEnergies(sense_energy=configuration._sense_energy, comm_energy=configuration._comm_energy)
pub_c.setThreshold(threshold=configuration._THRESHOLD_WINDOW)
pub_c.setObservationPeriod(period=configuration.OBSERVATION_PERIOD_MILISEC)
topic_c.setObservationPeriod(period=configuration.OBSERVATION_PERIOD_MILISEC)
# create capability matrix
    # dictionary with
        # key = topic
        # value = tuple (index of publishing device, [list of all capable devices])
system_capability = {}

#------------------------------------------#

# Precondition: all the topic strings are created
def createSystemCapability():
    capability = {topic: [-1, []] for topic in topic_c._topic_dict.keys()}
    for topic in topic_c._topic_dict.keys(): # for every topic
        for device in pub_c._devices._units.values(): # find the device
            if device.capableOfPublishing(topic):
                capability[topic][1].append(device._device_mac)
    return capability

#------------------------------------------#


def setup_exp_vary_pub():
    exp_num_pub = random.randint(3, configuration._max_pubs)
    topic_c.setupTopicStrings(numTopics=0)
    sub_c.setUpLatQoS(num_subs=0)
    pub_c.setupDevices(num_pubs=exp_num_pub)

#------------------------------------------#


def setup_exp_vary_sub():
    exp_num_subs = random.randint(3, configuration._max_subs)
    topic_c.setupTopicStrings(numTopics=0)
    sub_c.setUpLatQoS(num_subs=exp_num_subs)
    pub_c.setupDevices(num_pubs=0)

#------------------------------------------#

def setup_exp_vary_topic():
    exp_num_topics = random.randint(3, configuration._max_topics)
    topic_c.setupTopicStrings(numTopics=exp_num_topics)
    sub_c.setUpLatQoS(num_subs=0)
    pub_c.setupDevices(num_pubs=0)

#------------------------------------------#

def setup_default():
    topic_c.setupTopicStrings(numTopics=0)
    sub_c.setUpLatQoS(num_subs=0)
    pub_c.setupDevices(num_pubs=0)

#------------------------------------------#


# performed once before the rounds start
def experiment_setup():
    # based on the vary_xxx config settings, begin setup functions for the containers
    if configuration._vary_pubs:
        print("varying publishers")
        setup_exp_vary_pub()
    elif configuration._vary_subs:
        print("varying subscribers")
        setup_exp_vary_sub()        
    elif configuration._vary_topics:
        print("varying topics")
        setup_exp_vary_topic()
    else:
        print("using defaults")
        print("varying threshold")
        setup_default()
        #sys.exit()
    print("setting up timestamps")
    topic_c.setupSenseTimestamps()
    global system_capability 
    print("setting up system capability")
    system_capability = createSystemCapability()
    #print(system_capability)

#------------------------------------------#

# CSV Format for all files
    # algo_name, num_round, num_topic, num_pubs, num_subs, total_energy_consumption
def saveResults(algo_name:str, num_round, num_topic, num_pubs, num_subs, total_energy_consumption, time_end):
    if configuration._vary_pubs:
        file_path = file_paths["pub_path"] + filename + "pub"
    elif configuration._vary_subs:
        file_path = file_paths["sub_path"] + filename + "sub"
    elif configuration._vary_topics:
        file_path = file_paths["topic_path"] + filename + "topic"
    else:
        file_path = "results_lasting_time/" + filename + "obperiod_" + str(configuration.OBSERVATION_PERIOD_MILISEC) 
        #file_path = file_paths["threshold_path"] + filename + "thresh_" + str(configuration._THRESHOLD_WINDOW) 
    file_path = file_path + ".csv"
    data = [algo_name, time_end, num_round, num_topic, num_pubs, num_subs, total_energy_consumption]
    for device in pub_c._devices._units.keys():
        data.append(pub_c._devices._units[device]._consumption)
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

#------------------------------------------#

def getConsumption():
    totalConsumption = 0
    for deviceMac in pub_c._devices._units.keys():
        totalConsumption += pub_c._devices._units[deviceMac]._consumption
    return totalConsumption

#------------------------------------------#

def main():
    # create algo objects
    #rr = RR()
    #max_battery = MB()
    #min_task = MT()
    cc = MQTTCC()
    rand = Random()
    mqtt = Standard()
    global system_capability
    for round in range(configuration._sim_rounds):
        print("round number: ", round)
        # set up experiment
        experiment_setup()
        # set system capability and timestamps for algorithms
        #max_battery.copyOfSystemCapability(system_capability)
        #max_battery.copyOfTopicTimeStamps()
        #min_task.copyOfSystemCapability(system_capability)
        #min_task.copyOfTopicTimeStamps()
        rand.copyOfSystemCapability(system_capability)
        rand.copyOfTopicTimeStamps()    
        cc.copyOfSystemCapability(system_capability)
        cc.copyOfTopicTimeStamps()
        mqtt.copyOfSystemCapability(system_capability)
        mqtt.copyOfTopicTimeStamps()

# SIMULATE ALGORITHMS
# ====================
        # # run Min Task
        # min_task.min_task_algo()
        # # save the total energy consumption
        # pub_c._devices.calculateTotalEnergyConsumption()
        # mt_energy_consumption = pub_c._devices._all_devices_energy_consumption
        # #random.saveDevicesTotalEnergyConsumed(round_energy_consumption=rr_energy_consumption)
        # saveResults(algo_name=min_task._algo_name, num_round=round, num_topic=topic_c._total_topics, num_pubs=pub_c._total_devices, num_subs=sub_c._total_subs, total_energy_consumption=mt_energy_consumption)
        # # reset experiment for next algorithm
        # pub_c._devices.resetUnits()
        # pub_c._devices.clearAllDeviceEnergyConsumption()

# ====================

        # # run Max Battery 
        # max_battery.max_batt_algo()
        # # save the total energy consumption
        # pub_c._devices.calculateTotalEnergyConsumption()
        # mb_energy_consumption = pub_c._devices._all_devices_energy_consumption
        # #random.saveDevicesTotalEnergyConsumed(round_energy_consumption=rr_energy_consumption)
        # saveResults(algo_name=max_battery._algo_name, num_round=round, num_topic=topic_c._total_topics, num_pubs=pub_c._total_devices, num_subs=sub_c._total_subs, total_energy_consumption=mb_energy_consumption)
        # # reset experiment for next algorithm
        # pub_c._devices.resetUnits()
        # pub_c._devices.clearAllDeviceEnergyConsumption()

# ====================
        # # run RR 
        # rr.rr_algo()
        # # save the total energy consumption
        # pub_c._devices.calculateTotalEnergyConsumption()
        # rr_energy_consumption = pub_c._devices._all_devices_energy_consumption
        # #rr.saveDevicesTotalEnergyConsumed(round_energy_consumption=rr_energy_consumption)
        # saveResults(algo_name=rr._algo_name, num_round=round, num_topic=topic_c._total_topics, num_pubs=pub_c._total_devices, num_subs=sub_c._total_subs, total_energy_consumption=rr_energy_consumption)
        # # reset experiment for next algorithm
        # pub_c._devices.resetUnits()
        # pub_c._devices.clearAllDeviceEnergyConsumption()
# ====================
        # run random
        # timeEnd = rand.random_algo()
        # if timeEnd is None:
        #     timeEnd = "None"
        # # # # save the total energy consumption
        # # # #pub_c._devices.calculateTotalEnergyConsumption()
        # # # #random_energy_consumption = pub_c._devices._all_devices_energy_consumption
        # # # #random.saveDevicesTotalEnergyConsumed(round_energy_consumption=rr_energy_consumption)
        # totalConsumption = getConsumption()
        # saveResults(algo_name=rand._algo_name, time_end=timeEnd, num_round=round, num_topic=topic_c._total_topics, num_pubs=pub_c._total_devices, num_subs=sub_c._total_subs, total_energy_consumption=totalConsumption)
        
        # # # # reset experiment for next algorithm
        # pub_c._devices.resetUnits()
        # pub_c._devices.clearAllDeviceEnergyConsumption()
# ====================
        # run mqtt 
        timeEnd = mqtt.mqtt_algo()
        if timeEnd is None:
            timeEnd = "None"
        totalConsumption = getConsumption()
        saveResults(algo_name=mqtt._algo_name, time_end=timeEnd, num_round=round, num_topic=topic_c._total_topics, num_pubs=pub_c._total_devices, num_subs=sub_c._total_subs, total_energy_consumption=totalConsumption)
        pub_c._devices.resetUnits()
        pub_c._devices.clearAllDeviceEnergyConsumption()
# ====================
        # run mqtt-cc
        # cc.mqttcc_algo()
        # # save the total energy consumption
        # #pub_c._devices.calculateTotalEnergyConsumption()
        # #cc_energy_consumption = pub_c._devices._all_devices_energy_consumption
        # #cc.saveDevicesTotalEnergyConsumed(cc_energy_consumption)
        # #saveResults(algo_name=cc._algo_name, num_round=round, num_topic=topic_c._total_topics, num_pubs=pub_c._total_devices, num_subs=sub_c._total_subs, total_energy_consumption=cc_energy_consumption)
        # pub_c._devices.resetUnits()
        # pub_c._devices.clearAllDeviceEnergyConsumption()

# after running the algorithms, clear everything before next round
        pub_c._devices.clearUnits()
        pub_c._devices.clearAllDeviceEnergyConsumption()
        topic_c.clearTopicDict()
    print(last_msg)
    # after all the rounds, calculate the average system energy consumption per round
    # rr_avg_energy_consumption = rr._total_energy_consumption / configuration._sim_rounds
    # cc_avg_energy_consumption = cc._total_energy_consumption / configuration._sim_rounds
    # saveResults(algo_name=rr._algo_name, avg_energy_consumption=rr_avg_energy_consumption)
    # saveResults(algo_name=cc._algo_name, avg_energy_consumption=cc_avg_energy_consumption)

    # for loop num rounds
        # set up experiment 
        # run cc
        # reset anything in between algos
        # run rr
        # reset anyhting in between algos
    # run saveResults with algo + total_consumption / num_rounds

if __name__ == "__main__":
    main()
