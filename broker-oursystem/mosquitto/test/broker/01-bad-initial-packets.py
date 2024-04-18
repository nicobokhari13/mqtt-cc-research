#!/usr/bin/env python3

# Test whether non-CONNECT packets as an initial packet can cause excess memory use

from mosq_test_helper import *
import psutil

def write_config(filename, port):
    with open(filename, 'w') as f:
        f.write(f"listener {port}\n")
        f.write("allow_anonymous true\n")
        f.write("sys_interval 1\n")

def do_send(port, socks, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.append(sock)
    sock.connect(("127.0.0.1", port))
    try:
        sock.send(payload)
    except ConnectionResetError:
        pass

def do_test(port):
    rc = 1

    conf_file = os.path.basename(__file__).replace('.py', '.conf')
    write_config(conf_file, port)
    broker = mosq_test.start_broker(filename=os.path.basename(__file__), port=port, use_conf=True)

    try:
        socks = []

        do_send(port, socks, b"\x20\x80\x80\x80t" + b"\01"*100000000) # CONNACK
        do_send(port, socks, b"\x30\x80\x80\x80t" + b"\01"*100000000) # PUBLISH
        do_send(port, socks, b"\x40\x80\x80\x80t" + b"\01"*100000000) # PUBACK
        do_send(port, socks, b"\x50\x80\x80\x80t" + b"\01"*100000000) # PUBREC
        do_send(port, socks, b"\x60\x80\x80\x80t" + b"\01"*100000000) # PUBREL
        do_send(port, socks, b"\x70\x80\x80\x80t" + b"\01"*100000000) # PUBCOMP
        do_send(port, socks, b"\x80\x80\x80\x80t" + b"\01"*100000000) # SUBSCRIBE
        do_send(port, socks, b"\x90\x80\x80\x80t" + b"\01"*100000000) # SUBACK
        do_send(port, socks, b"\xA0\x80\x80\x80t" + b"\01"*100000000) # UNSUBSCRIBE
        do_send(port, socks, b"\xB0\x80\x80\x80t" + b"\01"*100000000) # UNSUBACK
        do_send(port, socks, b"\xC0\x80\x80\x80t" + b"\01"*100000000) # PINGREQ
        do_send(port, socks, b"\xD0\x80\x80\x80t" + b"\01"*100000000) # PINGRESP
        do_send(port, socks, b"\xE0\x80\x80\x80t" + b"\01"*100000000) # DISCONNECT
        do_send(port, socks, b"\xF0\x80\x80\x80t" + b"\01"*100000000) # AUTH

        mem = psutil.Process(broker.pid).memory_info().vms

        for s in socks:
            s.close()

        if os.environ.get('MOSQ_USE_VALGRIND') is None:
            limit = 25000000
        else:
            limit = 120000000
        if mem > limit:
            raise mosq_test.TestError(f"Process memory {mem} greater than limit of {limit}")

        rc = 0
    except MemoryError:
        print("Memory error!")
    except Exception as e:
        print(e)
    except mosq_test.TestError:
        pass
    finally:
        os.remove(conf_file)
        broker.terminate()
        broker.wait()
        (stdo, stde) = broker.communicate()
        if rc:
            print(stde.decode('utf-8'))
            exit(rc)


port = mosq_test.get_port()

do_test(port)

exit(0)
