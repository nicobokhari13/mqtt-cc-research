import random
import string

def generatePublisherMacs(numPubs):
    mac_chars = string.hexdigits[:-6]
    pub_macs = []
    for i in range(len(numPubs)):
        generated_mac = ''.join(random.choice(mac_chars) for _ in range(12)) 
        while generated_mac in pub_macs:
            generated_mac = ''.join(random.choice(mac_chars) for _ in range(12)) 
        pub_macs.append(generated_mac)
    print(pub_macs)
    return pub_macs

def generateDevicesFile(rows):
    pass

def generateDevicePublishings(deviceMac, topic_list):
    # need to generate (deviceMac, topic1, topic2,....) tuple
    list_of_publishing_rows = []
    num_capable = random.randrange(0, len(topic_list))
    for i in range(len(topic_list)):
        pass


