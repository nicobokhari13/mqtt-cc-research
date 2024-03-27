from algo_utils import Processing_Unit, Devices
import json
from proto_utils import ProtoUtils
from proto_db import Database

# types of generation
    # TODO: type 1: assigning topic that has a changed max_allowed or a new topic added to DB
    # TODO: type 2: complete reconfig after no new subscribers for some time
def generateAssignments():
    publishers = Devices()
    db = Database()
    db.openDB()
    bestMac = None
    Emin = None
    Einc = None
    Enew = None
    Eratio = None
    topicsWithNoPublishers = db.topicsWithNoPublishers() # list of tuples with (topic, max_allowed_latency)
    
    # get all topics where publish = 0 for all capable devices

    # for each topic with none publishing
    for task in topicsWithNoPublishers: 
        topic = task[0]
        freq = task[1]

        
        # get devices capable of publishing to the topic
        capableDevices = db.devicesCapableToPublish(topicName=topic) # list of tuples with (deviceMac, battery, executions)

        # for each device
        for device in capableDevices:
            mac = device[0]
            battery = device[1]
            num_exec = device[2]
            # get device publishing info with query
            devicePublishings = db.devicePublishing(MAC_ADDR=mac) # list of tuples with (topic, max_allowed_latency)

            # create processing unit at key = mac
            # add device info as a Processing_Unit in Devices singleton
            
            publishers.addProcessingUnit(Processing_Unit(macAddr=mac, capacity=battery, executions=num_exec))

            # add publishings to the device with macAddr = mac, and set device frequencies
            # add current device publishing info to assignments (topics that the device currently publishes to)
            publishers._units[mac].addPublishings(devicePublishings)

        # for each device in Devices singleton
        for macAddress, device in publishers._units.items:
            # Einc = device.energyIncrease(taskFrequency)

            Einc = device.energyIncrease(freq)
            # Enew = device.currentEnergy() + Einc
            Enew = device.currentEnergy() + Einc
            # Eratio = Enew / device.battery
            Eratio = Enew / device._battery
            # if (Enew <= device.battery && Eratio < Emin) or not Emin
                # bestMac = device._mac

            if (Enew <= device.battery and Eratio < Emin) or not Emin:
                bestMac = macAddress


        
        # if bestMac != None:
            # Devices[bestMac].addAssignnment(topic = topicName, task = topicFrequency)
            # Devices[bestMac]._num Executions = Emin / Devices[bestMac].ENERGY PER EXEC

        if bestMac != None:
                # adding the assignment adds the task's frequency to the publishings variable
                publishers._units[bestMac].addAssignment(topic, freq)
                publishers._units[bestMac]._numExecutions = Emin / publishers._units[bestMac]._ENERGY_PER_EXECUTION
    # by this point, all the devices in Devices have their list of assignments
    
    # for each device in Devices
        # if the assignments is not None:
            # assignmentString = json.dumps(device._assignments)
            # Devices.addAssignmentsToCommand(deviceMac = device._mac, taskList = assignmentString)
    for macAddress, device in publishers._units.items:
         if device._assignments is not None:
              assignmentString = json.dumps(device._assignments)
              publishers.addAssignmentsToCommand(deviceMac=macAddress, taskList=assignmentString)

    # the commands to send are in Devices._generated_cmd
    # return Devices._instance._generated_cmd
    return publishers._generated_cmd

# TODO 1: convert client to asyncio

def sendCommands(mapAssignments, client):
    # mapAssignments is a hash map with the schema:

    # macAddress: {"topic1/blah": 87, "topic2/ha": 85}
    # macAddress2: {"topic3/meh": 35}
    # ...
    # for each key in mapAssignments


    # commands are sent to the topic "sensor/cmd/" MAC_ADDR
    # so, for each device in the devices table, publish a message to
    # topic = "sensor/cmd/" + deviceMac
    # with payload = mapAssignments[deviceMac].dumps() since the value is a json object
    pass


# TODO: Probably put this in proto_utils since it will save the client? 
def sendCommandToDevice(client, macAddr, msg):
    # client.publish(topic = protoUtils.cmdTopic + macAddr, payload = msg)
    pass