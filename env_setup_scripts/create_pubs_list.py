import random
import string
import csv

def generatePublisherMacs(numPubs):
    pub_macs = []
    for i in range(numPubs):
        name = f"dev00{i}"
        pub_macs.append(name)
    print(pub_macs)
    return pub_macs

def createSimPublishersScript(deviceList: list, experiment_type):
    filePath = "./run_pubs.sh"
    lines = ["#!/bin/bash"]
    with open(filePath, 'w', newline='') as file:
        for row in deviceList: 
            line = f"python3 sensor.py {row[0]} {row[1]} {row[2]} {row[3]} {row[4]}"
            if row[0] == "MQTT":
                topics = ",".join(row[5:])
                line = line + f" {topics}"
            line = line + " &"
            lines.append(line)
        for row in lines:
            file.write(row + "\n")

        
def createTestBedPublishersScript(deviceList: list):
    for device in deviceList:
        filePath = f"./{device[1]}.sh"
        lines = ["cd .."]
        line = f"python3 sensor.py testbed {device[0]}"
        lines.append(line)
        with open(filePath, 'w', newline='') as file:
            for row in lines:
                file.write(row + "\n")

def generateDevicesFile(rows:list):
    filePath = "./devices.csv"
    with open(filePath, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows: 
            data = row
            writer.writerow(data)


def generateDevicePublishings(exp_type,deviceMac:str, topic_list:list, energy_per_execution, freq_range):
    # Example 
        # sim mac, battery, energy, 50
    row = [exp_type, deviceMac, 100, energy_per_execution, freq_range]
    unique_random_indices = set()
    num_capable = random.randint(1, len(topic_list)) # publish to 1 or all the topics
    while len(unique_random_indices) < num_capable:
        unique_random_indices.add(random.randrange(0, len(topic_list))) # choose an index between 0 and len(topic_list) - 1 
    for index in unique_random_indices:
        row.append(topic_list[index]) # append the topic to the row
        
    return row 


