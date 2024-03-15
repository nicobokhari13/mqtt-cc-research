import paho.mqtt.client as mqtt

def handle_status_msg(client, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print("Topic: " + topic)
    print("Received: " + payload)
