import asyncio
import socket
import sys 
import paho.mqtt.client as mqtt
import proto_utils
import proto_db as db
import status_handler as status
import will_topic_handler as will
import algo_handler as algo

class AsyncioHelper:
    def __init__(self, loop, client):
        self.loop = loop
        self.client = client
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):

        def cb():
            client.loop_read()

        self.loop.add_reader(sock, cb) 
        self.misc = self.loop.create_task(self.misc_loop())

    def on_socket_close(self, client, userdata, sock):
        self.loop.remove_reader(sock)
        self.misc.cancel()

    def on_socket_register_write(self, client, userdata, sock):

        def cb():
            client.loop_write()

        self.loop.add_writer(sock, cb) 
        
    def on_socket_unregister_write(self, client, userdata, sock):
        self.loop.remove_writer(sock)


    async def misc_loop(self):
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                print("in misc loop")
                await asyncio.sleep(1)                 
            except asyncio.CancelledError:
                break



class AsyncMqtt:
    def __init__(self, loop):
        self.loop = loop


    async def sendCommandToDevice(self, topic, msg):
        self.client.publish(topic, msg)
        print(f"sent to topic {topic}")

    async def sendCommands(self, mapAssignments:dict):
        print("sending commands")
        utils = proto_utils.ProtoUtils()
        command_threads = [self.sendCommandToDevice(topic=utils._CMD_TOPIC+macAddress, msg=cmd) for macAddress, cmd in mapAssignments] 
        await asyncio.gather(*command_threads)
        # resolve ranAlgo object
        print("finished sending commands")

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 5):
            sys.exit()
        utils = proto_utils.ProtoUtils()
        self.subscribeToTopics([utils._STATUS_TOPIC, utils._SUBS_WILL_TOPIC, utils._NEW_SUBS_TOPIC, utils._LAT_CHANGE_TOPIC])

    def subscribeToTopics(self, topics):
        for topic in topics:
            self.client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        utils = proto_utils.ProtoUtils()
        # Print MQTT message to console
        if mqtt.topic_matches_sub(utils._STATUS_TOPIC, topic):
            status.handle_status_msg(payload)
        if mqtt.topic_matches_sub(utils._SUBS_WILL_TOPIC, topic):
            will.updateDB(payload)
        if mqtt.topic_matches_sub(utils._NEW_SUBS_TOPIC, topic):
            # if there is a new topic, generate the new assignments
            mapAssignments = algo.generateAssignments()
            # resolve gotCmdToSend with the assignments
            utils._gotCmdToSend.set_result(mapAssignments)
        if mqtt.topic_matches_sub(utils._LAT_CHANGE_TOPIC, topic):
            # the message payload holds the topic with the changed max_allowed_latency
            # algo handler should still generateAssignemnts, must handle case where max allowed latency of topic changed
            mapAssignments = algo.generateAssignments(changedTopic=payload)
            utils._gotCmdToSend.set_result(mapAssignments)

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def waitForCommand(self):
        utils = proto_utils.ProtoUtils()
        mapAssignments = await utils._gotCmdToSend
        self.sendCommands(mapAssignments)

    async def waitForTimeWindow(self):
        utils = proto_utils.ProtoUtils()
        await asyncio.sleep(utils._timeWindow)
        # if time window is done first, resolve the got cmd to None
        print("ending window")
        utils._gotCmdToSend.set_result(None)

    async def main(self):
        # main execution        
        # get pub_utils singleton object
        utils = proto_utils.ProtoUtils()
        
        self.disconnected = self.loop.create_future()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        # set other necessary parameters for the client

        self.client.username_pw_set(username=utils._USERNAME, password=utils._PASSWORD)

        aioh = AsyncioHelper(self.loop, self.client)

        self.client.connect("localhost", 1883)

        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

        utils._gotCmdToSend = self.loop.create_future()
        print(utils._gotCmdToSend)

        while True: #infinite loop
            print("starting window")
            wait_for_cmd_routine = asyncio.create_task(self.waitForCommand())
            wait_for_window_routine = asyncio.create_task(self.waitForTimeWindow())

            done, pending = await asyncio.wait([wait_for_cmd_routine, wait_for_window_routine], return_when=asyncio.FIRST_COMPLETED)
            print("after await")
            # cancel what is still pending
            for task in pending:
                task.cancel()
            # gotCmdToSend will be resolved to either mapAssignments OR None
                
            if utils._gotCmdToSend: # if there are mapAssignments in the command
                # send command
                await self.sendCommands(utils._gotCmdToSend)

            else: # if _gotCmdToSend is None, then the time Window expired, must run algo again
                # reset publishings to 0 and executions to 0 
                algo.resetPublishingsAndDeviceExecutions()
                # run algo again
                mapAssignments = algo.generateAssignments()
                # send command
                await self.sendCommands(mapAssignments)

            utils._gotCmdToSend = self.loop.create_future()
            # TODO: await both utils._cmd and sleep(timeWindow) 
                # if sleep comes back first, then the algorithm did not run -> re run it
                # if cmd comes back first, then the algorithm ran, reset _gotCmdToSend 
def run_async_client():
    print("Starting")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncMqtt(loop).main())
    loop.close()
    print("Finished")

if __name__ == "__main__":
    run_async_client()

