import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish #publish dependency

SENSOR_ID = "1234"
STATUS_TOPIC = "status/" + SENSOR_ID
PUBLISH_TOPIC = "sensor/" + SENSOR_ID + "/temperature" + "%" + f"{ACCURACY_MIN}"

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
    client.subscribe(FIRE_ALARM_ER_TOPIC)
    print("Subscribed to topic: " + FIRE_ALARM_ER_TOPIC)

# The callback for when a message is published to the broker, and the backendreceives it
def on_message(client, userdata, msg):
    payload = str(msg.payload)
    topic = msg.topic
    # Print MQTT message to console
    print("From Topic: " + topic)
    print("Received: " + payload)
    usernameStart = (topic.rindex("/") + 1)
    print(f"Index of username: {usernameStart}")
    username = topic[usernameStart:]
    print(username)
    # Create Body for POST to PWA 
        # sub: Push Notification Subscription
        # notification: Contains fields that appear on native push notification
    data = {
    "username": username,
    "notification": {
        "title": "Fire Alarm Emergency", 
        "message": msg.payload.decode()
        }
    }   
    # Post data to PWA hosted at URL
    response = requests.post(PWA_PUSH_URL, json = data)
    print(response.status_code)
    if response:
        print(str(response))
    else:
        print("An error occured with the response") 

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
