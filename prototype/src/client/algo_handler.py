
def countExecutions(macAddr, newTaskFrequency):
    # get frequencies device is already publishing on
    # calculate # executions for frequencies within time period = max Frequency 
        # if within 1 minute of each other, remove
        # use least common multiple??? TODO: use lcm math, try examples
    # add newTaskFrequency  


    pass

def energyIncrease(macAddr, newTaskFrequency):
    num = countExecutions(macAddr = "deviceMac", newTaskFrequency = "max_allowed")
    energy = "constant"
    return energy * num
    pass

def generateAssignments():
    # variable to save best publisher's macAddr
    # get all topics from subscriptions table
    # get all devices + capabilities
    # loop over each topic
        # filter for devices capable of publishing to topic
        # filter out device already publishing to topic
        # loop over each device
            # eInc = energyIncrease(macAddr, newTaskFrequency)


    cmd = "message"
    return cmd

def sendCommands(mapAssignments, client):
    # mapAssignments is a hash map with the schema:

    # macAddress: {"topic1/blah": 87, "topic2/ha": 85}
    # macAddress2: {"topic3/meh": 35}
    # ...

    # commands are sent to the topic "sensor/cmd/" MAC_ADDR
    # so, for each device in the devices table, publish a message to
    # topic = "sensor/cmd/" + deviceMac
    # with payload = mapAssignments[deviceMac].dumps() since the value is a json object
    pass