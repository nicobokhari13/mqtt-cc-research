import paho.mqtt.client as mqtt
import status_handler as stts

USERNAME = "prototype"
PASSWORD = "adminproto"
STATUS_TOPIC = "status/#"
PUBLISH_TOPIC = "sensor/"
SUBS_WILL_TOPIC = "subs/will"

def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))
    if(rc == 5):
        print("Authentication Error on Broker")
        exit()
         
    client.subscribe(SUBS_WILL_TOPIC)
    print("Subscribed to topic: " + SUBS_WILL_TOPIC)

def on_message(client, userdata, msg):
    topic = msg.topiclear
    payload = msg.payload.decode()

    # Print MQTT message to console
    payload = msg.payload
    if mqtt.topic_matches_sub(STATUS_TOPIC, topic):
        stts.handle_status_msg(client, msg)
    if mqtt.topic_matches_sub(SUBS_WILL_TOPIC, topic):
        # TODO 2: create submodule for handling WILL_TOPIC, involves changing the database
        print(f"Topic: {topic}")
        print(f"Payload: {payload}")

# Executed when script is ran

def main():

    # TODO 1: create module to handle db connection, create tables before connecting to the broker

    # see gpt on this
    
    # Considering 3rd table be 
        # Device | Topic | Capability | Publishing
        # Devices are capable of publishing to many topics, and are publishing to at least 1

    # create MQTT Client
    client = mqtt.Client()
    # Set Paho API functions to our defined functions
    client.on_connect = on_connect
    client.on_message = on_message
    # Set username and password 
    client.username_pw_set(username=USERNAME, password=PASSWORD)
    # Connect client to the Broker
    client.connect("localhost", 1883)

    

    # Run cliet forever
    while True:
        client.loop()

if __name__ == "__main__":
    main()
