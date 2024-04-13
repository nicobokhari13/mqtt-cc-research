#!/bin/bash

# Path to the file containing PIDs (one PID per line)
pid_file="sub_pidfile.txt"

# Check if the file exists
if [ ! -f "$pid_file" ]; then
    echo "PID file $pid_file does not exist."
    exit 1
fi

# Read each line from the file and kill the corresponding process
while IFS= read -r pid; do
    if [ -n "$pid" ]; then
        echo "Killing process with PID $pid..."
        kill "$pid"
    fi
done < "$pid_file"
