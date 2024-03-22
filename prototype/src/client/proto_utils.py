
class ProtoUtils:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        self._USERNAME = "prototype"
        self._PASSWORD = "adminproto"
        self._STATUS_TOPIC = "sensor/status"
        self._CMD_TOPIC = "sensor/cmd/"
        self._timeWindow = 10
        self._WILL_TOPIC = "subs/will"
        self._SUBS_NET_LAT_TOPIC = "subs/netlat" # receive network lat from subs for some window of time
        self._network_latency_dict = dict()
        self._got_sub_net_lat = 0
        self._got_dev_status = 0
            # key = subbed_topic
            # value = list with [net lat sum, total # msgs]
    
    def setParameters(self, num_devices):
        self._numDevices = num_devices

    def initializeLatencyMap(self):
        for i in range(len(self._subtopics)):
            self._network_latency_dict[self._subtopics[i]] = [0,0]
        # Network Latency Matrix Example: 
        # {
        # /topic1: [network_latency_sum, total # msgs]
        # /topic2: [network_latency_sum, total # msgs]
        # /topic3: [network_latency_sum, total # msgs]
        # }
        # 

    def removeLatencyQoS(self):
        for i in range(len(self._subtopics)):
        # Remove %latency%
            latStringIndex = self._subtopics[i].rindex("%latency%")
            self._subtopics[i] = self._subtopics[i][:latStringIndex]
        

