import paho.mqtt.client as mqtt
import proto_db as db
from proto_utils import ProtoUtils
import json
import csv

utils = ProtoUtils()

def handle_status_msg(msg:str):
    database = db.Database()
    database.openDB()

    status_json = json.loads(msg)

    mac = status_json["deviceMac"]
    battery = status_json["battery"]
    time = status_json["time"]
    cpu_util_perc = status_json["cpu_utilization_percentage"]
    cpu_temp = status_json["cpu_temperature"]
    memory_util_perc= status_json["memory_utilization_percentage"]
    if "executions" in status_json.keys():
        num_executions = status_json["executions"]
    else: 
        num_executions = database.getNumExecutions(mac)
        num_executions = num_executions[0][0]

    logPublisherMetrics(time, mac, num_executions, battery, memory_util_perc, cpu_util_perc, cpu_temp)
    database.updateDeviceStatus(MAC_ADDR=mac, NEW_BATTERY=battery)
    database.closeDB()

def logPublisherMetrics(time, mac, num_executions, battery, memory_util_perc, cpu_util_perc, cpu_temp):
    logFile = utils._logFile 
    data = [time, mac, num_executions, battery, memory_util_perc, cpu_util_perc, cpu_temp]
    with open(logFile, 'a', newline='') as file:
        writer = csv.writer(file)
        
        # Append the data to the CSV file
        writer.writerow(data)
    