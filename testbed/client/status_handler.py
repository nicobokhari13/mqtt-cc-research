import paho.mqtt.client as mqtt
import proto_db as db
from proto_utils import ProtoUtils
import json
import csv
import psutil

utils = ProtoUtils()

def handle_status_msg(msg:str):
    database = db.Database()
    database.openDB()

    status_json = json.loads(msg)

    mac = status_json["deviceMac"]
    battery = status_json["battery"]
    time = status_json["time"]
    cpu_util_perc = getBrokerCpuUtil()
    cpu_temp = getBrokerCpuTemp()
    memory_util_perc= getBrokerMemoryUtil()
    utils.updateCapacities(mac, battery)
    num_executions = database.getNumExecutions(mac)
    num_executions = num_executions[0][0]
    if utils._exp_type == "testbed":
        logTestBedMetrics(time, mac, num_executions, battery, utils._remaining_batteries[mac], memory_util_perc, cpu_util_perc, cpu_temp)
    else:
        logPublisherMetrics(time, mac, battery, memory_util_perc, cpu_util_perc, cpu_temp)
    database.updateDeviceStatus(MAC_ADDR=mac, NEW_BATTERY=utils._remaining_batteries[mac])
    database.closeDB()

def logPublisherMetrics(time, mac, battery, memory_util_perc, cpu_util_perc, cpu_temp):
    logFile = utils._logFile 
    data = [time, mac, battery, memory_util_perc, cpu_util_perc, cpu_temp]
    with open(logFile, 'a', newline='') as file:
        writer = csv.writer(file)
        # Append the data to the CSV file
        writer.writerow(data)

def logTestBedMetrics(time, mac, executions, power_instant, remaining_power, memory_util_perc, cpu_util_perc, cpu_temp):
    logFile = utils._logFile_testbed
    data = [time, mac, executions, power_instant, remaining_power, memory_util_perc, cpu_util_perc, cpu_temp]
    with open(logFile, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def getBrokerCpuUtil():
    return psutil.cpu_percent(interval=1)

def getBrokerCpuTemp():
    return psutil.sensors_temperatures()['coretemp'][0].current
    
    #return psutil.sensors_temperatures()

def getBrokerMemoryUtil():
    return psutil.virtual_memory().percent