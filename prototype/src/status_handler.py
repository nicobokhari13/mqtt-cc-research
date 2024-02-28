import paho.mqtt.client as mqtt

def handle_status_msg(client, msg):
    topic = msg.topic
    payload = str(msg.payload)
    # Get username
    usernameStart = (topic.rindex("/") + 1)
    username = topic[usernameStart:]
    print("From: " + username)
    print("Topic: " + topic)
    print("Received: " + payload)
