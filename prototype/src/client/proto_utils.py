
class ProtoUtils:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        self._USERNAME = "prototype"
        self._PASSWORD = "adminproto"
        # Device handling topics
        self._STATUS_TOPIC = "sensor/status"
        self._CMD_TOPIC = "sensor/cmd/"
        
        # Subscriber handling topics
        self._SUBS_WILL_TOPIC = "subs/will"
        self._NEW_SUBS_TOPIC = "subs/add" 
        self._LAT_CHANGE_TOPIC = "subs/change"

        # Other vars 
        self._timeWindow = 3600
        self._ranAlgo = None
        self._gotStatus = None
        self._gotWill = None

