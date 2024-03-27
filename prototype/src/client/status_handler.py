import paho.mqtt.client as mqtt
import proto_db as db

def handle_status_msg(msg):
    database = db.Database()
    database.openDB()
    # example status
    # status_json = {
    #     "MAC_ADDR": utils._MAC_ADDR,
    #     "BATTERY": utils._battery,
    # }
    topic = msg.topic
    payload = msg.payload.decode()
    print("Topic: " + topic)
    print("Received: " + payload)
