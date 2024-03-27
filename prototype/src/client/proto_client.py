import paho.mqtt.client as mqtt
import proto_db as db
import proto_utils
import sys
import csv
from proto_asyncio import run_async_client

# USERNAME = "prototype"
# PASSWORD = "adminproto"
# STATUS_TOPIC = "status/#"
# PUBLISH_TOPIC = "sensor/"
# SUBS_WILL_TOPIC = "subs/will"
# NEW_SUBS_TOPIC = "subs/add" 
# LAT_CHANGE_TOPIC = "subs/change"

# def on_connect(client, userdata, flags, rc):

#     print("Connected with result code "+str(rc))
#     if(rc == 5):
#         print("Authentication Error on Broker")
#         sys.exit()
         
# def on_message(client, userdata, msg):
#     topic = msg.topic
#     payload = msg.payload.decode()

#     # Print MQTT message to console
#     if mqtt.topic_matches_sub(STATUS_TOPIC, topic):
#         status.handle_status_msg(client, msg)
#     if mqtt.topic_matches_sub(SUBS_WILL_TOPIC, topic):
#         will.updateDB(payload)
#     if mqtt.topic_matches_sub(NEW_SUBS_TOPIC, topic):
#         mapAssignments = algo.generateAssignments()
#         algo.sendCommands(mapAssignments, client)
#         pass
#     if mqtt.topic_matches_sub(LAT_CHANGE_TOPIC, topic):
#         # the message payload holds the topic with the changed max_allowed_latency
#         # algo handler should still generateAssignemnts, must handle case where max allowed latency of topic changed
#         mapAssignments = algo.generateAssignments(changedTopic=payload)
#         algo.sendCommands(mapAssignments, client)
#         pass

    
# Executed when script is ran

def main():
    devicesFile = sys.argv[1]
    database = db.Database()
    database.openDB()
    database.createDeviceTable()
    database.createPublishTable()
    try:
        with open(devicesFile, 'r', newline='') as devfile:
            reader = csv.reader(devfile)
            rows = list(reader)
    except FileNotFoundError:
        print("File not found ", devicesFile)
        sys.exit()
    # if exp, ignore first two attributes of devices.txt row
    for i in range(len(rows)):
        startBattery = rows[i][2]
        mac = rows[i][3]
        database.addDevice(MAC_ADDR=mac, BATTERY=startBattery)
        topicList = rows[i][4:len(rows[i])] # rest of rows are the topics
        for topic in topicList:
            database.addDeviceTopicCapability(MAC_ADDR=mac, TOPIC=topic)
    database.closeDB()
    utils = proto_utils.ProtoUtils()
    run_async_client()

if __name__ == "__main__":
    main()
