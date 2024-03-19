import asyncio
import socket
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

        self.loop.add_reader(sock, cb) # every time the socket is readable, call the calback function cb()
        self.misc = self.loop.create_task(self.misc_loop())

    def on_socket_close(self, client, userdata, sock):
        print("Socket closed")
        self.loop.remove_reader(sock)
        print("after removing reader")
        self.misc.cancel()

    def on_socket_register_write(self, client, userdata, sock):
        print("Watching socket for writability.")

        def cb():
            print("on_socket_register_write callback: Socket is writable, calling loop_write")
            client.loop_write()
            print("after loop_write")

        self.loop.add_writer(sock, cb) # invoke the callback cb when the socket is available for writing

    def on_socket_unregister_write(self, client, userdata, sock):
        print("on_socket_unregister_write: Stop watching socket for writability.")
        self.loop.remove_writer(sock)
        print("after removing writer")

    async def misc_loop(self):
        print("misc_loop started")
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                print("loop_misc going to sleep")
                await asyncio.sleep(1)
                print("in misc loop: after await sleep")
            except asyncio.CancelledError:
                print("asyncio Cancelled Error")
                break
        print("misc_loop finished")


class AsyncMqttExample:
    def __init__(self, loop):
        self.loop = loop

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect: Subscribing")
        client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        if not self.got_message:
            print("Got unexpected message: {}".format(msg.decode()))
        else:
            # when await self.got_message is called, this function resolves that async
            print("received msg, resolving await")
            self.got_message.set_result(msg.payload)

    def on_disconnect(self, client, userdata,rc):
        self.disconnected.set_result(rc)

    async def main(self):
        self.disconnected = self.loop.create_future()
        self.got_message = None

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        aioh = AsyncioHelper(self.loop, self.client)

        print("connecting to server")
        self.client.connect('mqtt.eclipseprojects.io', 1883, 60)
        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
        for c in range(3):
            print(f"main loop {c}")
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


print("Starting")
loop = asyncio.get_event_loop()
loop.run_until_complete(AsyncMqttExample(loop).main())
loop.close()
print("Finished")
