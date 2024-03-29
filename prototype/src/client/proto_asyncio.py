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
        utils = proto_utils.ProtoUtils()._instance
        command_threads = [self.sendCommandToDevice(topic=utils._CMD_TOPIC+macAddress, msg=cmd) for macAddress, cmd in mapAssignments.items()] 
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
        utils = proto_utils.ProtoUtils()._instance
        print("in on_message")
        #print(f"utils is {utils}")
        #print(f"gotCmdToSend = {utils._gotCmdToSend}")
        print(f"gotCmdToSend = {self.got_message}")
        # Print MQTT message to console
        if mqtt.topic_matches_sub(utils._STATUS_TOPIC, topic):
            print("in status handler")
            status.handle_status_msg(payload)
        if mqtt.topic_matches_sub(utils._SUBS_WILL_TOPIC, topic):
            print("in will handler")
            will.updateDB(payload)
        if mqtt.topic_matches_sub(utils._NEW_SUBS_TOPIC, topic):
            print("in new subs handler")
            # if there is a new topic, generate the new assignments
            mapAssignments = algo.generateAssignments()
            #print(f"cmd object = {utils._gotCmdToSend}")
            print(f"cmd object = {self.got_message}")
            # resolve gotCmdToSend with the assignments
            # if not utils._gotCmdToSend:
            #     print("cmd object is none tf")
            if not self.got_message:
                print("cmd object is none tf")
            print("before setting assignments")
            #utils._gotCmdToSend.set_result(mapAssignments)
            self.got_message.set_result(mapAssignments)
            print("after setting assignments")
        if mqtt.topic_matches_sub(utils._LAT_CHANGE_TOPIC, topic):
            # the message payload holds the topic with the changed max_allowed_latency
            # algo handler should still generateAssignemnts, must handle case where max allowed latency of topic changed
            print("in lat change handler")
            mapAssignments = algo.generateAssignments(changedTopic=payload)
            #print(f"cmd object = {utils._gotCmdToSend}")
            print(f"cmd object = {self.got_message}")
            # if not utils._gotCmdToSend:
            #     print("cmd object is none tf")
            if not self.got_message:
                print("cmd object is none tf")
            print("before setting assignments")
            #utils._gotCmdToSend.set_result(mapAssignments)
            self.got_message.set_result(mapAssignments)
            print("after setting assignments")

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def waitForCommand(self):
        #utils = proto_utils.ProtoUtils._instance
        #print(f"utils is {utils}")
        print("waiting for command")
        #print(f"gotCmdToSend = {utils._gotCmdToSend}")
        print(f"gotCmdToSend = {self.got_message}")
        # wait for gotCmdToSend to be set from on_message
        #command = await utils._gotCmdToSend
        command = await self.got_message
        print("got command")
        return command


    async def waitForTimeWindow(self):
        utils = proto_utils.ProtoUtils()._instance
        print("waiting for time window")
        await asyncio.sleep(utils._timeWindow)
        # if time window is done first, resolve the got cmd to None
        print("ending window")
        return None

    async def main(self):
        # main execution        
        # get pub_utils singleton object
        utils = proto_utils.ProtoUtils()._instance
        
        self.disconnected = self.loop.create_future()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.got_message = None
        # set other necessary parameters for the client

        self.client.username_pw_set(username=utils._USERNAME, password=utils._PASSWORD)

        aioh = AsyncioHelper(self.loop, self.client)

        self.client.connect("localhost", 1883)

        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

        while True: #infinite loop
            #utils._gotCmdToSend = self.loop.create_future()
            self.got_message = self.loop.create_future()
            #print(f"starting window and set gotCmdToSend = {utils._gotCmdToSend}")
            print(f"starting window and set gotCmdToSend = {self.got_message}")
            wait_for_cmd_routine = asyncio.create_task(self.waitForCommand())
            wait_for_window_routine = asyncio.create_task(self.waitForTimeWindow())

            done, pending = await asyncio.wait([wait_for_cmd_routine, wait_for_window_routine], return_when=asyncio.FIRST_COMPLETED)
            print("after await")
            result = done.pop().result()
            if result: # if result exists, then result holds the commad
                # cancel what is still pending
                for task in pending:
                    task.cancel()
                await self.sendCommands(result)
                # utils._gotCmdToSend = None
                self.got_message = None
            else: # if result is None, then the time Window expired, must run algo again
                # reset publishings to 0 and executions to 0 
                for task in pending:
                    task.cancel()
                algo.resetPublishingsAndDeviceExecutions()
                # run algo again
                mapAssignments = algo.generateAssignments()
                # send command
                await self.sendCommands(mapAssignments)
                self.got_message = None

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

