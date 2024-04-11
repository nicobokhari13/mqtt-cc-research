#!/bin/bash
python3 sensor.py sim 1 2 3 4 &
python3 sensor.py MQTT 11 12 13 14 15,16 &
python3 sensor.py MQTT 21 22 23 24 25,26,27 &
