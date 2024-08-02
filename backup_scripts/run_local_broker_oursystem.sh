#!/bin/bash

cd /home/devnico/repos/research/mqtt_cc_research/broker-oursystem/mosquitto

make binary

# Check if make command was successful
if [ $? -eq 0 ]; then
    # Execute mosquitto with the provided configuration file
    pwd
    ./src/mosquitto -v -c mqtt_cc.conf
else
    echo "Make command failed. Exiting..."
    exit 1

cd ..

fi