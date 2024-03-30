from algo_utils import Processing_Unit, Devices
import json
from proto_utils import ProtoUtils
from proto_db import Database

def resetPublishingsAndDeviceExecutions():
    db = Database()
    db.openDB()
    db.resetPublishings()
    db.resetDeviceExecutions()
    db.closeDB()

def generateAssignments(changedTopic = None):
    db = Database()
    db.openDB()
    if changedTopic:
        db.resetDevicesPublishingToTopic(changedTopic)
        # if there was a change in a topic's max_allowed_latency,
        # find all the devices that currently publish to the topic and set publishing = 0
        # then run algorithm exactly the same as it will be treated like it was just added to the DB
    publishers = Devices()

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
        print(f"Task: {task}")
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
            print(f"{mac}, {battery}, {num_exec}")
                
            publishers.addProcessingUnit(Processing_Unit(macAddr=mac, capacity=battery, executions=num_exec))

            # add publishings to the device with macAddr = mac, and set device frequencies
            # add current device publishing info to assignments (topics that the device currently publishes to)
            print(f"publishings {devicePublishings}")

            # if there are topics the device already publishes to
            if devicePublishings:
                # add them to the unit
                publishers._units[mac].addPublishings(devicePublishings)

                if changedTopic and topic == changedTopic:
                    # if there was a latency change to changedTopic, then you must recalculate devices' number of executions
                    publishers._units[mac].resetExecutions()

        # for each device in Devices singleton
        for macAddress, device in publishers._units.items():
            # determine the energy incrase for adding the topic's frequency to the device
            print(f"checking energy increase on {macAddress} from adding {freq}")
            Einc = device.energyIncrease(freq)
            print(f"Energy increased on {macAddress} {Einc}")

            # the device's new energy level after addition of the topic
            Enew = device.currentEnergy() + Einc
            print(f"{macAddress}'s energy after increase = {Enew}")
            # the device's new energy level divided by its available battery
            Eratio = Enew / device._battery
            print(f"ratio of new Energy / current Battery = {Eratio}")
            # if the new energy level is less than the battery, and 
            # the new energy level's ratio to the battery is smaller than the min 
            if not Emin:
                bestMac = macAddress
                Emin = Eratio
            elif (Enew <= device._battery and Eratio < Emin):
                bestMac = macAddress
                Emin = Eratio
            print(f"best Mac = {bestMac}")

        
        
        # if bestMac != None:
            # Devices[bestMac].addAssignnment(topic = topicName, task = topicFrequency)
            # Devices[bestMac]._num Executions = Emin / Devices[bestMac].ENERGY PER EXEC

        if bestMac != None:
                # adding the assignment adds the task's frequency to the publishings variable
                publishers._units[bestMac].addAssignment(topic, freq)
                # we know bestMac uses Emin energy, so reverse operations to get Einc
                Einc = (Emin * publishers._units[bestMac]._battery) - publishers._units[bestMac].currentEnergy()
                changeInExecutions = Einc / Processing_Unit._ENERGY_PER_EXECUTION
                print(f"{bestMac} used to execute at {publishers._units[bestMac]._numExecutions}")
                New_Executions = changeInExecutions + publishers._units[bestMac]._numExecutions
                print(f"{bestMac} now executes at {New_Executions}")
                publishers._units[bestMac]._numExecutions = New_Executions
                # update num executions in DB
                db.updateDeviceExecutions(MAC_ADDR=bestMac, NEW_EXECUTIONS=New_Executions)

    # by this point, all the devices in Devices have their list of assignments
    
    # for each device in Devices
        # if the assignments is not None:
            # assignmentString = json.dumps(device._assignments)
            # Devices.addAssignmentsToCommand(deviceMac = device._mac, taskList = assignmentString)
    for macAddress, device in publishers._units.items():
        if device._assignments:
            assignmentString = json.dumps(device._assignments)
            print(f"assignment string = {assignmentString}")
            publishers.addAssignmentsToCommand(deviceMac=macAddress, taskList=assignmentString)
            db.updatePublishTableWithPublishingAssignments(MAC_ADDR=macAddress, TOPICS=device._assignments.keys()) 
    db.closeDB()
    publishers.resetUnits()
    print(f"generated final command = {publishers._generated_cmd}")
    # while the publishers' unit information is reset, the assignments are preserved in generated_cmd
    return publishers._generated_cmd

