
class SubscriberUtils:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self, subbed_topics, time_window) -> None:
        self._subtopics = subbed_topics # (list of topics)
        self._msgCount = 0
        self._timeWindow = time_window
        self._WILL_TOPIC = "subs/will"
        self._SUBS_NET_LAT_TOPIC = "subs/netlat" # receive network lat from subs for some window of time
        self._network_latency_dict = dict()
            # key = subbed_topic
            # value = list with [avg net lat, total # msgs]
        self._newMsgCount = [[]] # a list of accumulated msgs

        pass
