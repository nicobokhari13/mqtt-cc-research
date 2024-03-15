import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish 
import time
import random
import json

SENSOR_ID = "1234"
sample_frequency_ms = 100 # ms 
MS_TO_SECONDS_DIVIDER = 1000

STATUS_TOPIC = "status/" + SENSOR_ID
BROKER_HOST = "localhost"
TEMP_TOPIC = "sensor/temperature"
USERNAME = "dev01"
PASSWORD = "mqttccd1"

def handle_command(brokerCommand):
    print(brokerCommand)
# TODO 2: Refactor like subscriber.py to take in command line arg for credentials, topics able to publish to

# TODO 2: Add time stamps to mqtt messages
def on_connect(clinet, userdata, flags, rc):
    if(rc == 5):
        print("Broker Authentication Error")
        exit()
    print(f"Connected to Broker with result code {rc}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"Topic: {topic}")
    print(f"Message: {payload}")

def main():
    temperatureData = 32
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username=USERNAME, password= PASSWORD)
    client.connect("localhost", 1883)

    while True: 
        client.loop()
        temperatureData = random.randint(0, 100)
        client.publish(topic=TEMP_TOPIC, payload=str(temperatureData))
        time.sleep(sample_frequency_ms / MS_TO_SECONDS_DIVIDER) # publish temperature every 100ms

if __name__ == "__main__":
    main()




