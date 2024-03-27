import paho.mqtt.client as mqtt
import proto_db as db
import json

def handle_status_msg(msg:str):
    database = db.Database()
    database.openDB()
    # example status
    # status_json = {
    #     "MAC_ADDR": utils._MAC_ADDR,
    #     "BATTERY": utils._battery,
    # }
    status_json = json.loads(msg)
    database.updateDeviceStatus(MAC_ADDR=status_json["deviceMac"], NEW_BATTERY=status_json["battery"])
    database.closeDB()
