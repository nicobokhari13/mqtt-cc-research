import asyncio
import socket
import sys 
import paho.mqtt.client as mqtt

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

                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break

    def pubilshToTopics(self):
        pass


class AsyncMqtt:
    def __init__(self, loop):
        self.loop = loop

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 5):
            sys.exit()
        # After connect, subscribe to CMD topic
        # client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        # if the topic matches the cmd topic, resolve got_cmd with set_result
        if not self.got_message:
            print("Got unexpected message: {}".format(msg.decode()))
        else:
            # when await self.got_message is called, this function resolves that async
            print("received msg, resolving await")
            self.got_message.set_result(msg.payload)

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def main(self):
        # main execution

        # get pub_utils singleton object

        self.disconnected = self.loop.create_future()
        self.got_message = None

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        # set other necessary parameters for the client

        aioh = AsyncioHelper(self.loop, self.client)

        self.client.connect("localhost", 1883)

        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)


        while True: #infinite loop
            # await asyncio.sleep(timewindow)

            # create lock object

                # async with lock

                # update pub_utils object with current battery

            # publish status to status topic

            # create future for got_cmd

            # await got_cmd

            # create lock object

                # async with lock
                # in cmd, get new pub topics with mac address
            
                # change pub_utils publishing topics

            # set got_cmd to None


            await asyncio.sleep(5)
            print("main: Publishing")
            self.got_message = self.loop.create_future()
            self.client.publish(topic, b'Hello' * 40000, qos=1)
            print("waiting for msg")
            msg = await self.got_message
            print("main: Got response with {} bytes".format(len(msg)))
            self.got_message = None

        self.client.disconnect()
        print("main: Disconnected: {}".format(await self.disconnected))

def run_async_publisher():
    print("Starting")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncMqtt(loop).main())
    loop.close()
    print("Finished")

if __name__ == "__main__":
    run_async_publisher()

