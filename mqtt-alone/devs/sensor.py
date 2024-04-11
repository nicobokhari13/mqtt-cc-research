import paho.mqtt.client as mqtt
import sys # command line parameters
import pub_utils
from pub_asyncio import run_async_publisher
import psutil
import json
import random

# python3 sensor.py sim <username> <password> <startBattery> <MACAddress>
def main():
    frequency_range = None
    topics = None
    utils = pub_utils.PublisherUtils()
    # extract input parameters
    if(sys.argv[1] == "sim" or sys.argv[1] == "MQTT"):
        # params for sim
            # sim macAddr battery energy freq_range(0)


        #print("Using default credentials and topics for subscriber")
        #USERNAME = sys.argv[2]
        #PASSWORD = sys.argv[3]
        MacAddr = sys.argv[2]
        battery = sys.argv[3]
        energy = sys.argv[4]
        if sys.argv[1] == "MQTT":
            frequency_range = int(sys.argv[5])
            topics = sys.argv[6].split(",") # list of topic strings
            # the example input params
                # python3 sensor.py sim dev001 100 0.1 50 topic/1,topic/2,topic/3
                # params for MQTT
                    # MQTT macAddress battery energy freq_range topics_list
    
        simValue = True
    else:
        #USERNAME = sys.argv[1]
        #PASSWORD = sys.argv[2]
        MacAddr = sys.argv[2]
        battery = psutil.sensors_battery().percent
        simValue = False
    
        # topic list delimited by commas, no spaces
    # create single instance of pub_utils with cmd line parameters
    utils.setParameters(Mac_addr=MacAddr, start_battery=battery, in_sim=simValue, energy_per_execution=energy)
    if sys.argv[1] == "MQTT":
        utils.randomizePublishes(frequency_range, topics)
         
    # move execution to pub_asyncio
    run_async_publisher()

if __name__ == "__main__":
    main()





