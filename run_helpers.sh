#!/bin/bash

mosquitto_sub -u dev03 -P mqttccd3 -v -t subs/change &
mosquitto_sub -u dev04 -P mqttccd4 -v -t subs/add &

wait