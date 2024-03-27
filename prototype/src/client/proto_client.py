import paho.mqtt.client as mqtt
import proto_db as db
import status_handler as status
import will_topic_handler as will
import algo_handler as algo
import sys

USERNAME = "prototype"
PASSWORD = "adminproto"
STATUS_TOPIC = "status/#"
PUBLISH_TOPIC = "sensor/"
SUBS_WILL_TOPIC = "subs/will"
NEW_SUBS_TOPIC = "subs/add" 
LAT_CHANGE_TOPIC = "subs/change"

def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))
    if(rc == 5):
        print("Authentication Error on Broker")
        sys.exit()
         
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    # Print MQTT message to console
    if mqtt.topic_matches_sub(STATUS_TOPIC, topic):
        status.handle_status_msg(client, msg)
    if mqtt.topic_matches_sub(SUBS_WILL_TOPIC, topic):
        will.updateDB(payload)
    if mqtt.topic_matches_sub(NEW_SUBS_TOPIC, topic):
        mapAssignments = algo.generateAssignments()
        algo.sendCommands(mapAssignments, client)
        pass
    if mqtt.topic_matches_sub(LAT_CHANGE_TOPIC, topic):
        # the message payload holds the topic with the changed max_allowed_latency
        # algo handler should still generateAssignemnts, must handle case where max allowed latency of topic changed
        mapAssignments = algo.generateAssignments(changedTopic=payload)
        algo.sendCommands(mapAssignments, client)
        pass

    
# Executed when script is ran

def main():
    database = db.Database()
    database.openDB()
    database.createDeviceTable()
    database.createPublishSelectTable()
    database.closeDB()

    
    # create MQTT Client
    client = mqtt.Client()
    # Set Paho API functions to our defined functions
    client.on_connect = on_connect
    client.on_message = on_message
    # Set username and password 
    client.username_pw_set(username=USERNAME, password=PASSWORD)
    # Connect client to the Broker
    client.connect("localhost", 1883)

    # Run cliet forever
    while True:
        client.loop()

if __name__ == "__main__":
    main()
