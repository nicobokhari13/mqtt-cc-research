
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
        
        # TODO: Put Prototype client in here to use 

