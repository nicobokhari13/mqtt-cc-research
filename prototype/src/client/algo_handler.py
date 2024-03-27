from algo_utils import Processing_Unit, Devices
import json
from proto_utils import ProtoUtils

# types of generation
    # TODO: type 1: assigning topic that has a changed max_allowed or a new topic added to DB
    # TODO: type 2: complete reconfig after no new subscribers for some time
def generateAssignments():
    publishers = Devices()
    bestMac = None
    Emin = None
    Einc = None
    Enew = None
    Eratio = None
    # get all topics where publish = 0 for all capable devices

    # for each topic with none publishing
        # get devices capable of publishing to the topic
    
        # for each device
            # add device info as a Processing_Unit in Devices singleton
            # get device publishing info with query
        
        # for each device in Devices singleton
            # Einc = device.energyIncrease(taskFrequency)
            # Enew = device.currentEnergy() + Einc
            # Eratio = Enew / device.battery
            # if (Enew <= device.battery && Eratio < Emin) or not Emin
                # bestMac = device._mac
        
        # if bestMac != None:
            # Devices[bestMac].addAssignnment(topic = topicName, task = topicFrequency)
            # Devices[bestMac]._num Executions = Emin / Devices[bestMac].ENERGY PER EXEC
    
    # by this point, all the devices in Devices have their list of assignments
    
    # for each device in Devices
        # if the assignments is not None:
            # assignmentString = json.dumps(device._assignments)
            # Devices.addAssignmentsToCommand(deviceMac = device._mac, taskList = assignmentString)
    
    # the commands to send are in Devices._generated_cmd
    # return Devices._instance._generated_cmd
    pass 

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