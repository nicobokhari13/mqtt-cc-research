import paho.mqtt.client as mqtt
import sys # command line parameters
import pub_utils
from pub_asyncio import run_async_publisher
import psutil

# python3 sensor.py sim <username> <password> <startBattery> <MACAddress>
def main():
    # extract input parameters
    if(sys.argv[1] == "sim"):
        #print("Using default credentials and topics for subscriber")
        USERNAME = sys.argv[2]
        PASSWORD = sys.argv[3]
        battery = sys.argv[4]
        MacAddr = sys.argv[5]
        energy = sys.argv[6]
        simValue = True
    else:
        USERNAME = sys.argv[1]
        PASSWORD = sys.argv[2]
        battery = psutil.sensors_battery().percent
        MacAddr = sys.argv[3]
        simValue = False
        # topic list delimited by commas, no spaces
    # create single instance of pub_utils with cmd line parameters
    utils = pub_utils.PublisherUtils()
    utils.setParameters(username=USERNAME, password=PASSWORD,Mac_addr=MacAddr, start_battery=battery, in_sim=simValue, energy_per_execution=energy)
    # move execution to pub_asyncio
    run_async_publisher()

if __name__ == "__main__":
    main()





