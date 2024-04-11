import random 

topics = ["/topic/0", "/topic/1", "/topic/2"]
deviceList = [
    ["deviceMac", "/topic/0"],
    ["deviceMac2", "/topic/1"]
]

found = False
for topic in topics:
    for device in deviceList: 
        if topic in device:
            found = True
            break 
        else: 
            found = False
    if found: # if the topic was found, continue to the next topic
        print("topic already covered")
        continue
    else: # else, add the topic to a random device
        print(f"the {topic} is not covered")
        randomDeviceIndex = random.randrange(0, len(deviceList))
        deviceList[randomDeviceIndex].append(topic)
        print(f"added topic to {deviceList[randomDeviceIndex]}")

print(deviceList)