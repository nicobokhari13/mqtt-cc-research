import asyncio
import socket
import sys 
import paho.mqtt.client as mqtt
import pub_utils
import psutil
import json
from datetime import datetime

class AsyncioHelper:
    def __init__(self, loop, client):
        self.loop = loop
        self.client = client
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write
        self.start_up = True

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
        utils = pub_utils.PublisherUtils()
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                print("starting window")
                await asyncio.sleep(utils._timeWindow)
                print("end window, sending status now")
                # create lock object
                lock = asyncio.Lock()
                async with lock:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"time {current_time}")
                    utils._battery = utils._battery - 2
                    # utils._battery = psutil.sensors_battery().percent
                    print(f"battery: {utils._battery}")

                    status_json = {
                        "deviceMac": utils._MAC_ADDR,
                        "battery": utils._battery,
                        "time": current_time
                    }
                    status_str = json.dumps(status_json)
                    # publish status to status topic
                    print("publishing status")
                    self.client.publish(topic = utils._STATUS_TOPIC, payload = status_str)            
            except asyncio.CancelledError:
                break



class AsyncMqtt:
    def __init__(self, loop):
        self.loop = loop

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 5):
            sys.exit()
        utils = pub_utils.PublisherUtils()
        client.subscribe(utils._CMD_TOPIC)
        # After connect, subscribe to CMD topic

    async def waitForCmd(self):
        #utils = pub_utils.PublisherUtils()
        #await utils._got_cmd 
        cmd = await self.got_message
        return cmd


    def on_message(self, client, userdata, msg):
        utils = pub_utils.PublisherUtils()
        # if the topic matches the cmd topic, resolve got_cmd with set_result
        if mqtt.topic_matches_sub(msg.topic, utils._CMD_TOPIC):
            print(f"{utils._deviceMac} received command: {msg.payload.decode()}")
            # utils._got_cmd.set_result(msg.payload.decode())
            self.got_message.set_result(msg.payload.decode())

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)
    
    async def publish_to_topic(self, sense_topic, freq):
        utils = pub_utils.PublisherUtils()
        msg = "data"
        self.client.publish(topic = sense_topic, payload = msg)
        await asyncio.sleep(freq)
        print(f"device {utils._deviceMac} finished publish to {sense_topic} on frequency {freq}")
        return (sense_topic, freq)
    
    async def main(self):
        # main execution        
        # get pub_utils singleton object
        utils = pub_utils.PublisherUtils()
        self.disconnected = self.loop.create_future()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message 
        self.client.on_disconnect = self.on_disconnect
        # TODO: Use self.got_message instead of utils._got_cmd
        self.got_message = None
        # set other necessary parameters for the client
        self.client.username_pw_set(username=utils._USERNAME, password=utils._PASSWORD)

        aioh = AsyncioHelper(self.loop, self.client)

        self.client.connect("localhost", 1883)

        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
        #utils._got_cmd = self.loop.create_future()
        
        self.got_message = self.loop.create_future()
        
        if not utils._publishes: 
            # if nothing to publish yet (at start up)
            print("waiting for publish")
            # cmd = await utils._got_cmd # wait for command to come
            cmd = await self.got_message # wait for command to come
            # once we have command, set publishings
            utils.setPublishing(json.loads(cmd))
            # create sensing_task routines
            routines = [self.publish_to_topic(topic, freq) for topic,freq in utils._publishes.items()]
            # reset command
            #utils._got_cmd = self.loop.create_future()
            self.got_message = self.loop.create_future()
            # tasks are the publishing tasks assigned to the publisher
            tasks = [asyncio.create_task(coro) for coro in routines]
            # also add waiting for command from prototype
            tasks.append(asyncio.create_task(self.waitForCmd()))

        while True: #infinite loop
            try:
                print("running tasks")
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                # run the tasks until 1 completes

                # get the "returned" value from the done task
                result = done.pop().result()
                # sensing tasks return None, waitForCmd returns the command

                print(f"task result = {result}")
                # if the result is a tuple, then a sensing task was done
                if isinstance(result, tuple):
                    print(f"sensing task {result} done, running it again")
                    #tasks.append(asyncio.create_task(self.publish_to_topic(sense_topic=result[0], freq=result[1])))

                else:
                    print("result is command")
                    print("canceling other tasks")
                    # cancel other sensing tasks
                    for unfinished_task in pending:
                        unfinished_task.cancel()
                    print("changing tasks")
                    utils.setPublishing(json.loads(result))
                    routines = [self.publish_to_topic(topic, freq) for topic,freq in utils._publishes.items()]
                    tasks = [asyncio.create_task(coro) for coro in routines]
                    tasks.append(asyncio.create_task(self.waitForCmd()))
                    # reset got cmd
                    #utils._got_cmd = self.loop.create_future()
                self.got_message = self.loop.create_future()
                    # tasks are the publishing tasks assigned to the publisher
                    # also add waiting for command from prototype
            except asyncio.CancelledError:
                print("asyncio cancelled")

def run_async_publisher():
    print("Starting")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncMqtt(loop).main())
    loop.close()
    print("Finished")

if __name__ == "__main__":
    run_async_publisher()

