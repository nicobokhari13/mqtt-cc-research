import sys
import create_topics_list as ct
import create_subs_list as cs
import create_pubs_list as cp
import random 

def main():
    # example input 
        # sim 10 20 3 0.1 40 900 10
    experiment_type = sys.argv[1]
    num_subs = int(sys.argv[2])
    num_topics = int(sys.argv[3])
    threshold = int(sys.argv[4])
    energy_per_execution = float(sys.argv[5])  
    frequency_range = int(sys.argv[6])
    if experiment_type != "MQTT":
        algo_window = sys.argv[7]
    
    if experiment_type != "testbed":
        num_pubs = int(sys.argv[8])
    else: 
        num_pubs = 0



    print(f"{algo_window} {experiment_type} {num_subs} {num_topics} {threshold} {energy_per_execution} {frequency_range}")
    # Create topics
    topics = ct.createTopicList(num_topics)

    print(topics)

    # create subscribers + their subscriptions + 
    subscribers = cs.generateSubscriberNames(num_subs)
    subscriber_command_rows = []
    for sub_name in subscribers:
        if experiment_type == "MQTT":
            # if base MQTT, then do not use publisher selection or latency QoS
            subscriber_command_rows.append(cs.generateSubscriptions(sub_name, topics, frequency_range = 0))
        else: 
            subscriber_command_rows.append(cs.generateSubscriptions(sub_name, topics, frequency_range))
    print(subscriber_command_rows)
    deviceList = []
    # if num_pubs defined (i.e, a simulation)
    if num_pubs:
        pub_macs = cp.generatePublisherMacs(num_pubs)
    else:
        pub_macs = ["d8:3a:dd:90:ee:38", "d8:3a:dd:90:ee:62"]
    for mac in pub_macs:
        deviceList.append(cp.generateDevicePublishings(experiment_type, mac, topics, energy_per_execution, frequency_range))
    print(deviceList, sep="\n")
    print(deviceList)
    # Double check every topic is assigned at least 1 publisher
    found = False
    for topic in topics: # for ecah topi 
        for device in deviceList: # loop over the devices
            if topic in device: # check if the topic is in the device
                found = True 
                print("found topic {topic}")
                break # if so, move on
            else: 
                found = False 
        if found: # if the topic was found, continue to the next topic
            continue
        else: # else, add the topic to a random device
            print("adding missing topic to device")
            randomDeviceIndex = random.randrange(0, len(deviceList))
            deviceList[randomDeviceIndex].append(topic)
    print(deviceList, sep="\n")
    
    # create Devices.csv
    cp.generateDevicesFile(deviceList)
    # create scripts
    cs.createSubscriberCSV(subscriber_command_rows)
    if experiment_type == "testbed":
        cp.createTestBedPublishersScript(deviceList)
    else:
        cp.createSimPublishersScript(deviceList)
    ct.createClientScript(experiment_type, algo_window, energy_per_execution, threshold)
    



    



    


    

if __name__ == "__main__":
    main()