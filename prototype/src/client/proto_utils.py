from datetime import datetime
class ProtoUtils:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("instance is None, creating new one")
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        self._USERNAME = "prototype"
        self._PASSWORD = "adminproto"
        # Device handling topics
        self._STATUS_TOPIC = "sensor/status" # subscribe
        self._CMD_TOPIC = "sensor/cmd/" # publish
        
        # Subscriber handling topics
        self._SUBS_WILL_TOPIC = "subs/will" # subscribe 
        self._NEW_SUBS_TOPIC = "subs/add" # subscribe
        self._LAT_CHANGE_TOPIC = "subs/change" # subscribe

        # Other vars 
        self._timeWindow = 3600
        # self._ranAlgo = None
        self._gotStatus = None
        self._gotCmdToSend = None

        self._logFile = "metrics-" + str(datetime.now()) + ".csv"
        
        self._in_sim = False

