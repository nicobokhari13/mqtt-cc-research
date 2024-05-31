
deviceList = [
    ["sim", "1", "2", "3", "4"],
    ["MQTT", "11", "12", "13", "14", "15", "16"],
    ["MQTT", "21", "22", "23", "24", "25", "26", "27"],
]
def createSimPublishersScript(deviceList: list):
    filePath = "./run_pubs.sh"
    lines = ["#!/bin/bash"]
    with open(filePath, 'w', newline='') as file:
        for row in deviceList: 
            line = f"python3 sensor.py {row[0]} {row[1]} {row[2]} {row[3]} {row[4]}"
            if row[0] == "MQTT":
                topics = ",".join(row[5:])
                line = line + f" {topics}"
            line = line + " &"
            lines.append(line)
        for row in lines:
            file.write(row + "\n")

createSimPublishersScript(deviceList)