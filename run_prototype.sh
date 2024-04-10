#!/bin/bash

cd /home/devnico/repos/research/mqtt_cc_research/prototype/src/client
python3 proto_client.py /home/devnico/repos/research/mqtt_cc_research/prototype/src/devs/devices.csv sim 900 5
# <path to device csv> <sim/exp boolean value> <restart_window> <energy per execution> <concurrency threshold>
