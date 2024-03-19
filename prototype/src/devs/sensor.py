# import paho.mqtt.client as mqtt
# import paho.mqtt.publish as publish 
# import time
# import random
# import json

# SENSOR_ID = "1234"
# sample_frequency_ms = 100 # ms 
# MS_TO_SECONDS_DIVIDER = 1000

# STATUS_TOPIC = "status/" + SENSOR_ID
# BROKER_HOST = "localhost"
# TEMP_TOPIC = "sensor/temperature"
# USERNAME = "dev01"
# PASSWORD = "mqttccd1"

# def handle_command(brokerCommand):
#     print(brokerCommand)

# # TODO 2: Add time stamps to mqtt messages
# def on_connect(clinet, userdata, flags, rc):
#     if(rc == 5):
#         print("Broker Authentication Error")
#         exit()
#     print(f"Connected to Broker with result code {rc}")


# def on_message(client, userdata, msg):
#     topic = msg.topic
#     payload = msg.payload.decode()
#     print(f"Topic: {topic}")
#     print(f"Message: {payload}")

# def main():
#     temperatureData = 32
#     client = mqtt.Client()
#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.username_pw_set(username=USERNAME, password= PASSWORD)
#     client.connect("localhost", 1883)

#     while True: 
#         client.loop()
#         temperatureData = random.randint(0, 100)
#         client.publish(topic=TEMP_TOPIC, payload=str(temperatureData))
#         time.sleep(sample_frequency_ms / MS_TO_SECONDS_DIVIDER) # publish temperature every 100ms

# if __name__ == "__main__":
#     main()

import paho.mqtt.client as mqtt
import sys # command line parameters
import json # structure reading and time
import time # for timestamp variable 

SUBS_NET_LAT_TOPIC = "subs/netlat" # receive network lat from subs for some window of time



# The callback for when the client receives a CONNACK response from the broker.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
    if(rc == 5):
        #print("Authentication Error on Broker")
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

# python3 subscriber.py <username> <password>
def main():
    publishing_topics = []
    if(sys.argv[1] == "default"):
        #print("Using default credentials and topics for subscriber")
        USERNAME = "sub01"
        PASSWORD = "mqttcc01"
        subbed_topics = ["sensor/temperature%latency%80", "sensor/airquality%latency%65"]
    elif(len(sys.argv) < 4 or len(sys.argv) > 5):
        print(f"Error: incorrect number of command line parameters. {len(sys.argv)} Expected username, password, and topics list")
        sys.exit()
    else:
        USERNAME = sys.argv[1]
        PASSWORD = sys.argv[2]
        # topic list delimited by commas, no spaces
        subbed_topics = sys.argv[3].split(",") # list of strings 
    # create MQTT Client
    client = mqtt.Client()
    # Set Paho API functions to our defined functions
    client.on_connect = on_connect
    client.on_message = on_message
    # Set username and password 
    client.username_pw_set(username=USERNAME, password=PASSWORD)
    will_data = {
        "clientid":USERNAME, 
        "topics": subbed_topics
        }
    will_payload = json.dumps(will_data)
    client.will_set(topic=WILL_TOPIC, payload=will_payload, qos=1)
    # Connect client to the Broker
    client.connect("localhost", 1883)
    subscribeToTopics(client, topicList = subbed_topics)

    # Run cliet forever
    while True:
        client.loop()

if __name__ == "__main__":
    main()





