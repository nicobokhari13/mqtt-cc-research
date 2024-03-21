#!/bin/bash

# Run mosquitto_pub command, ignore errors, and redirect stdout/stderr to /dev/null
mosquitto_pub -u internal -P mqttcci -t subs/change -m 1 >/dev/null 2>&1
