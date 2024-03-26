
def countExecutions(macAddr, newTaskFrequency):
    # get frequencies device is already publishing on
    # make it a set to remove duplicates

    pass

def energyIncrease(macAddr, newTaskFrequency):
    num = countExecutions(macAddr = "deviceMac", newTaskFrequency = "max_allowed")
    energy = "constant"
    return energy * num

# types of generation
    # TODO: type 1: assigning topic that has a changed max_allowed or a new topic added to DB
    # TODO: type 2: complete reconfig after no new subscribers for some time
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