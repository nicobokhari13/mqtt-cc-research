import csv

deviceList = [
    ["sim", "1", "2", "3", "4"],
    ["MQTT", "11", "12", "13", "14", "15", "16"],
    ["MQTT", "21", "22", "23", "24", "25", "26", "27"],
]

def generateDevicesFile(rows:list):
    filePath = "./devices.csv"
    with open(filePath, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows: 
            data = row
            writer.writerow(data)

generateDevicesFile(deviceList)