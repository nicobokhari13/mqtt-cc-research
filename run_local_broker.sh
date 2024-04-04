#!/bin/bash

cd /home/devnico/repos/research/broker/mosquitto-2.0.18

make

# Check if make command was successful
if [ $? -eq 0 ]; then
    # Execute mosquitto with the provided configuration file
    pwd
    ./src/mosquitto -v -c mqtt_cc_local.conf
else
    echo "Make command failed. Exiting..."
    exit 1

cd ..

fi