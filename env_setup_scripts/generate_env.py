import os
import sys
import csv

def main():
    experiment_type = sys.argv[1]
    num_subs = sys.argv[2]
    num_topics = sys.argv[3]
    threshold = sys.argv[4]
    energy_per_execution = sys.argv[5]  
    frequency_range = sys.argv[6]

    if experiment_type != "MQTT":
        time_window = sys.argv[7]
    if experiment_type == "testbed":
        device_01 = sys.argv[8]
        device_01 = sys.argv[9]
    if experiment_type != "testbed":
        num_pub = sys.argv[8]


    

if __name__ == "__main__":
    main()