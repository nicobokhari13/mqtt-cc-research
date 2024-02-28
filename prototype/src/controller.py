import paho.mqtt.client as mqtt
import status_handler as stts

USERNAME = "prototype"
PASSWORD = "adminproto"
STATUS_TOPIC = "status/#"
PUBLISH_TOPIC = "sensor/"

# BROKER_HOST = "mqtt.eclipseprojects.io"

# The callback for when the client receives a CONNACK response from the broker.
def on_connect(client, userdata, flags, rc):

    # print("Connected to Broker. Result Code: "+str(rc))
    if(rc == 5):
        print("Authentication Error on Broker")
        exit()
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # subscribing to FireAlarm topic
    client.subscribe(STATUS_TOPIC)
    print("Subscribed to topic: " + STATUS_TOPIC)

# The callback for when a message is published to the broker, and the backendreceives it
def on_message(client, userdata, msg):
    topic = msg.topic
    # Print MQTT message to console

    if mqtt.topic_matches_sub(STATUS_TOPIC, topic):
        stts.handle_status_msg()

# Executed when script is ran

def main():

    # create MQTT Client
    client = mqtt.Client()
    # Set Paho API functions to our defined functions
    client.on_connect = on_connect
    client.on_message = on_message
    # Set username and password 
    client.username_pw_set(username=CLIENT_USERNAME, password=CLIENT_PASSWORD)
    # Connect client to the Broker
    client.connect("localhost", 1883)

    # Run cliet forever
    while True:
        client.loop()

if __name__ == "__main__":
    main()
