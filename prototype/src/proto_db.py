import sqlite3

class Database:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        self._db_path = "/home/devnico/repos/research/sqlite/mqttcc.db"

    def openDB(self) -> None:
        self._db_conn = sqlite3.connect(self._db_path)
        self._db_cursor = self._db_conn.cursor()

    def closeDB(self) -> None:
        self._db_cursor.close()
        self._db_conn.close()

    # TODO: Add database lock error handling so if a sqlite3.OperationalError is raised, delay for some time, then retry the execution
        # A generic function with query, values, maxRetries, delay, etc (see GPT)
    
    def execute_query_with_retry(self, query:str, values = None, requires_commit=False, max_retries=3, delay = 0.1 ):
        pass

    def createDeviceTable(self) -> None:
        self._db_cursor.execute('''CREATE TABLE IF NOT EXISTS devices (
                                deviceMAC TEXT PRIMARY KEY, 
                                battery FLOAT)''')
        self._db_conn.commit()

    def createPublishSelectTable(self) -> None:
        self._db_cursor.execute('''
                                CREATE TABLE IF NOT EXISTS publish_select (
                                deviceMAC TEXT, 
                                topic TEXT, 
                                capability BOOLEAN,
                                publish BOOLEAN,
                                FOREIGN KEY (deviceMAC) REFERENCES devices(deviceMAC),
                                FOREIGN KEY (topic) REFERENCES subscriptions(topic) 
                                PRIMARY KEY (deviceMAC, topic)
                                )''')
        self._db_conn.commit()

    def selectSubscriptionsWithTopic(self, topic):
        self._db_cursor.execute('''SELECT * FROM subscriptions WHERE topic = ?''', (topic,))
        # cursor has rows represented as tuples

    def updateSubscriptionWithLatency(self, topic, new_lat_qos, new_max_lat):
        print(f"Topic: {topic}")
        print(f"Latency Req: {new_lat_qos}")
        print(f"Max Allowed Latency: {new_max_lat}")
        values = (new_lat_qos, new_max_lat, topic)
        update_query = '''UPDATE subscriptions SET latency_req = ?, max_allowed_latency = ? WHERE topic = ?'''
        self._db_cursor.execute(update_query, values)      
        # Commit changes
        self._db_conn.commit()  

    




    
        
