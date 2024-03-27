import paho.mqtt.client as mqtt
import proto_db as db
import json
import csv

def handle_status_msg(msg:str, time):
    database = db.Database()
    database.openDB()
    # example status
    # status_json = {
    #     "MAC_ADDR": utils._MAC_ADDR,
    #     "BATTERY": utils._battery,
    # }
    mac = status_json["deviceMac"]
    battery = status_json["battery"]
    status_json = json.loads(msg)
    logPublisherBattery(mac, battery, time)
    database.updateDeviceStatus(MAC_ADDR=mac, NEW_BATTERY=battery)
    database.closeDB()

def logPublisherBattery(mac, battery, time):
    logFile = "batteries.csv" 
    data = [time, mac, battery]
    with open('batteries.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        
        # Append the data to the CSV file
        writer.writerow(data)
    