import paho.mqtt.client as mqtt
import sys # command line parameters
import json # structure will & network latency msg
import time

SUBS_NET_LAT_TOPIC = "subs/netlat" # receive network lat from subs for some window of time
WILL_TOPIC = "subs/will"

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
    print(f"Topic: {topic}")
    print(f"Message: {payload}")
    print()

def subscribeToTopics(client, topicList:list):
    for topic in topicList:
        print(f"Subscribing to {topic}")
        client.subscribe(topic)
        #print("sleeping now")
        #time.sleep(16)
# Executed when script is ran

# python3 subscriber.py <username> <password>
def main():
    subbed_topics = []
    if(sys.argv[1] == "default"):
        #print("Using default credentials and topics for subscriber")
        USERNAME = "sub01"
        PASSWORD = "mqttcc01"
        subbed_topics = ["sensor/temperature%latency%80", "sensor/airquality%latency%65"]
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
