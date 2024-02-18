import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish 
import random
import json

SENSOR_ID = "1234"
ACCURACY_MIN = 95 # percentage
sample_frequency = 450 # megahertz 

STATUS_TOPIC = "status/" + SENSOR_ID
PUBLISH_TOPIC = "sensor/" + SENSOR_ID + "/temperature" + "%" + f"{ACCURACY_MIN}"
COMMAND_TOPIC = "command/" + SENSOR_ID
BROKER_HOST = "localhost"
CLIENT_USERNAME = "user01"
CLIENT_PASSWORD = "password"

def handle_command(brokerCommand):
    print(brokerCommand)


def on_connect(clinet, userdata, flags, rc):
    if(rc == 5):
        print("Broker Authentication Error")
        exit()
    print(f"Connected to Broker with result code {rc}")


def on_message(client, userdata, msg):
    if(msg.topic == COMMAND_TOPIC):
        handle_command(msg)
    else: 
        print(msg.topic+" "+str(msg.payload))


def main():
    accuracy = 0
    temperatureData = 32
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username=CLIENT_USERNAME, password=CLIENT_PASSWORD)
    client.connect("localhost", 1883)

    while True: 
        client.loop()
        accuracy = random.randint(90, 100)
        print(f"Current accuracy: {accuracy}")
        status_data = {
            "id": SENSOR_ID, 
            "accuracy": accuracy,
            "frequency": sample_frequency,
            "topic": STATUS_TOPIC
        }
        status_json = json.dumps(status_data)
        publish.single(STATUS_TOPIC, status_json, hostname = BROKER_HOST, auth={'username':CLIENT_USERNAME, 'password':CLIENT_PASSWORD})
        time.sleep(5)





