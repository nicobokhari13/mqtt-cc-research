#!/bin/bash

cd /home/devnico/repos/research/prototype/src/devs
python3 sensor.py sim dev01 mqttccd1 100 b8:27:eb:4f:15:95 &
python3 sensor.py sim dev02 mqttccd2 95 a8:20:dc:2d:51:59


 