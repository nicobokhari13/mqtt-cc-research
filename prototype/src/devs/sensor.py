import paho.mqtt.client as mqtt
import sys # command line parameters
import json # structure reading and time
import time # for timestamp variable 
import pub_utils
from pub_asyncio import run_async_publisher

# python3 sensor.py <username> <password> <startBattery> <sampleFrequency> <MACAddress> <list of topics separated by comma>
def main():
    # extract input parameters
    if(sys.argv[1] == "default"):
        #print("Using default credentials and topics for subscriber")
        USERNAME = "dev01"
        PASSWORD = "mqttccd1"
        battery = 100.0
        sampleFrequency = 10 # sample frequency is provided in cmd, on start up, must wait for cmd
        MacAddr = "b8:27:eb:4f:15:95"
        publishing_topics = ["sensor/airquality"]
    elif(len(sys.argv) != 7):
        print(f"Error: incorrect number of command line parameters. {len(sys.argv)} Expected username, password, startBattery, sampleFrequency, MACAddress, and topics list")
        sys.exit()
    else:
        USERNAME = sys.argv[1]
        PASSWORD = sys.argv[2]
        battery = sys.argv[3]
        MacAddr = sys.argv[4]
        publishing_topics = sys.argv[5].split(",") # list of strings 
        # topic list delimited by commas, no spaces
    # create single instance of pub_utils with cmd line parameters
    utils = pub_utils.PublisherUtils()
    utils.setParameters(username=USERNAME, password=PASSWORD, pub_topics=publishing_topics, Mac_addr=MacAddr, start_battery=battery)
    # move execution to pub_asyncio
    run_async_publisher()

if __name__ == "__main__":
    main()





