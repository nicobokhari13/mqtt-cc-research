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

    async def publish_to_topic(self, sense_topic, freq):
        msg = "data"
        print(f"publishing to topic {sense_topic}")
        self.client.publish(topic = sense_topic, payload = msg)
        print("waiting for sample_freq")
        await asyncio.sleep(freq)

    async def misc_loop(self):
        utils = pub_utils.PublisherUtils()
        utils._got_cmd = self.loop.create_future()
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                if(self.start_up):
                    cmd = await utils._got_cmd
                    utils.setPublishing(json.loads(cmd))
                    self.start_up = False
                publish_to_topic = [self.publish_sensing(topic, freq) for topic,freq in utils._publishes]
                await asyncio.gather(*publish_to_topic)                    
            except asyncio.CancelledError:
                break



class AsyncMqtt:
    def __init__(self, loop):
        self.loop = loop

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 5):
            sys.exit()
        # After connect, subscribe to CMD topic
        # client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        utils = pub_utils.PublisherUtils()
        # if the topic matches the cmd topic, resolve got_cmd with set_result
        if mqtt.topic_matches_sub(msg.topic, utils._CMD_TOPIC):
            utils._got_cmd.set_result(msg.payload.decode()) 

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def main(self):
        # main execution        
        # get pub_utils singleton object
        utils = pub_utils.PublisherUtils()
        
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


        while True: #infinite loop
            # await asyncio.sleep(timewindow)
            print("starting window")
            await asyncio.sleep(utils._timeWindow)
            
            # create lock object
            lock = asyncio.Lock()
            async with lock:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                utils._battery = psutil.sensors_battery().percent
                print(f"battery: {utils._battery}")

            status_json = {
                "deviceMac": utils._MAC_ADDR,
                "battery": utils._battery,
                "time": current_time
            }

            status_str = json.dumps(status_json)

            # publish status to status topic

            self.client.publish(topic = utils._STATUS_TOPIC, payload = status_str)

            # create future for got_cmd
            utils._got_cmd = self.loop.create_future()

            # await got_cmd
            await utils._got_cmd 
            
            # create lock object
            lock = asyncio.Lock()

                # async with lock
            async with lock:
                if(utils._got_cmd):
                    cmd_dict = json.loads(utils._got_cmd)
                    # in cmd, get new pub topics with mac address
                    # change pub_utils publishing topics
                    utils._pubtopics = cmd_dict[utils._MAC_ADDR]
                    print(utils._pubtopics)
                    print(type(utils._pubtopics))
                    # set got_cmd to None
                    utils._got_cmd = None

def run_async_publisher():
    print("Starting")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncMqtt(loop).main())
    loop.close()
    print("Finished")

if __name__ == "__main__":
    run_async_publisher()

