import paho.mqtt.client as mqtt
import sys # command line parameters
import json # structure reading and time
import time # for timestamp variable 
import pub_utils
from pub_asyncio import run_async_publisher

# The callback for when the client receives a CONNACK response from the broker.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
    if(rc == 5):
        print("Authentication Error on Broker")
        exit()

# The callback for when a message is published to the broker, and the backendreceives it
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    #print(f"Topic: {topic}")
    #print(f"Message: {payload}")
    #print()

def subscribeToTopics(client, topicList:list):
    for topic in topicList:
        #print(f"Subscribing to {topic}")
        client.subscribe(topic)
# Executed when script is ran

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
        sampleFrequency = sys.argv[4]
        MacAddr = sys.argv[5]
        publishing_topics = sys.argv[6].split(",") # list of strings 
        # topic list delimited by commas, no spaces
    # create single instance of pub_utils with cmd line parameters
    utils = pub_utils.PublisherUtils()
    utils.setParameters(username=USERNAME, password=PASSWORD, pub_topics=publishing_topics, sample_frequency=sampleFrequency, Mac_addr=MacAddr, start_battery=battery)
    # move execution to pub_asyncio
    run_async_publisher()

if __name__ == "__main__":
    main()





