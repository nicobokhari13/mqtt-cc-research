#!/bin/bash
if [ $# -eq 0 ]; then
exit 1
fi
file_path="$1"
if [ ! -f "$file_path" ]; then
exit 1
fi
python3 proto_client.py "$file_path" MQTT 3 0 0.2
