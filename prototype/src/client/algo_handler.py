
def countExecutions(macAddr, newTaskFrequency):
    # get frequencies device is already publishing on
    # make it a set to remove duplicates

    # TODO: Track number of executions + execution changes. Make class that holds macAddr, execution #, set of frequencies publishing

    pass

def energyIncrease(macAddr, newTaskFrequency):
    num = countExecutions(macAddr = "deviceMac", newTaskFrequency = "max_allowed")
    energy = "constant"
    return energy * num

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