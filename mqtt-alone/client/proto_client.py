import paho.mqtt.client as mqtt
import proto_db as db
from proto_utils import ProtoUtils
import sys
import csv
from proto_asyncio import run_async_client
#from algo_utils import Devices
from datetime import datetime
import status_handler

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

    
# data in each row of devices.csv
    # exp_type, deviceMac, battery, energy_per_execution, freq_range, topic publishings
    # 1         2           3           4                   5           6  -> ...
def main():
    utils = ProtoUtils()
    # to run proto_client.py 
        # devicesFile sim 900 0.1 3
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    devicesFile = sys.argv[1]
    in_sim = sys.argv[2]
    restart_window = sys.argv[3] # in seconds
    energy_per_execution = sys.argv[4] 
    threshold = sys.argv[5]
    
    print(f"Device File = {devicesFile}")
    print(f"Sim Value = {in_sim}")
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
    # loop through devices.csv
    # row = exp_type, deviceMac, 100, energy_per_execution, freq_range
    for i in range(len(rows)):
        mac = rows[i][1]
        startBattery = rows[i][2]
        database.addDevice(MAC_ADDR=mac, BATTERY=startBattery)
        status_handler.logPublisherMetrics(time=current_time, mac=mac, battery=startBattery, num_executions=0, memory_util_perc="None", cpu_util_perc="None", cpu_temp="None")
        topicList = rows[i][5:len(rows[i])] # rest of rows are the topics
        for topic in topicList:
            database.addDeviceTopicCapability(MAC_ADDR=mac, TOPIC=topic)
    database.closeDB()
    # create it once
#    devices = Devices()
#    devices.addEnergyPerExecution(energy_per_execution)
#    devices.addConcurrencyThreshold(threshold)
#    utils._timeWindow = int(restart_window)
    if in_sim == "sim" or in_sim == "MQTT":
        utils._in_sim = True
    elif in_sim == "testbed": 
        utils._in_sim = False
    else: 
        print("Error with determining experiment type, exiting now")
        sys.exit()
    print(f"in_sim {utils._in_sim}")
    run_async_client()

if __name__ == "__main__":
    main()
