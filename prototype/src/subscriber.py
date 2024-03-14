import paho.mqtt.client as mqtt
import sys # command line parameters
import json # structure will & network latency msg

# TODO 2: Calculate average network latency from timestamps in received messages for each topic
    # Essentially a m X 3 matrix where m = # topics. 
    # In the first column, the name of the topic is stored. 
    # In the second column, the average network latency
    # In the third column, the total number of messages received
    # To update the average, 
        # multiply the current average by the total # of msgs
        # add the latency difference from the recent message
        # increment the total # of msgs
        # divide the new latency sum by new total # msgs
    # Send only columns 1 and 2 to the client after the time window 
    # This matrix is created when the run_subs.py script inputs the topics from subscribers.txt 
        # matrix will be used to determine topic matching in on_message
        # consider using accumulated_msgs variable that is reset after time window
        # so the latency calculations are performed only once per time window pre-determined at start up script
        # use singleton? 
#TEMP_TOPIC = "sensor/temperature"
WILL_TOPIC = "subs/will"
SUBS_REQ_NET_LAT = "subs/req"
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
    # refactor to perform a different action if the proto_client sends a msg asking about netlatency
    #print(f"Topic: {topic}")
    #print(f"Message: {payload}")
    #print()
    if(mqtt.topic_matches_sub(sub=topic, topic=SUBS_REQ_NET_LAT)):
        #print("exiting program")
        with open("subs.txt", "a") as file:
            file.write(f"exiting program {sys.argv[1]}")
        sys.ex
def subscribeToTopics(client, topicList:list):
    for topic in topicList:
        #print(f"Subscribing to {topic}")
        client.subscribe(topic)
# Executed when script is ran

# python3 subscriber.py <username> <password>
def main():
    subbed_topics = []
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
        subbed_topics = sys.argv[3].split(",")
        #print(subbed_topics)
    print(f"starting subscriber {USERNAME}")
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
    client.subscribe(SUBS_REQ_NET_LAT)
    subscribeToTopics(client, topicList = subbed_topics)

    # Run cliet forever
    while True:
        client.loop()

if __name__ == "__main__":
    main()
