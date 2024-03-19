import sqlite3
import time

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

    def execute_query_with_retry(self, query:str, values = None, requires_commit=False, max_retries=3, delay = 0.1 ):
        for i in range(max_retries):
            try: 
                cursor = self._db_conn.cursor()
                if values:
                    cursor.execute(query, values)
                else:
                    cursor.execute(query)
                if requires_commit:
                    self._db_conn.commit()
                return cursor.fetchall() # if the command does not return rows, then empty list is returned
            except sqlite3.OperationalError as err:
                if "database is locked" in str(err):
                    print(f"Database is locked. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    raise
        raise sqlite3.OperationalError("Max retries exceeded. Unable to execute query.")
        

    def createDeviceTable(self) -> None:
        deviceTable = '''CREATE TABLE IF NOT EXISTS devices (
                                deviceMAC TEXT PRIMARY KEY, 
                                battery FLOAT, 
                                sample_frequency_ms INTEGER)'''
        self.execute_query_with_retry(query=deviceTable, requires_commit=True)

    def createPublishSelectTable(self) -> None:
        publishSelectTable = '''
                                CREATE TABLE IF NOT EXISTS publish_select (
                                deviceMAC TEXT, 
                                topic TEXT, 
                                capability BOOLEAN,
                                publish BOOLEAN,
                                FOREIGN KEY (deviceMAC) REFERENCES devices(deviceMAC),
                                FOREIGN KEY (topic) REFERENCES subscriptions(topic) 
                                PRIMARY KEY (deviceMAC, topic)
                                )'''
        # capability: True = can publish, False = cannot publish
        # publish: True = is currently publishing to topic, False = is not currently publishing
        self.execute_query_with_retry(query=publishSelectTable, requires_commit=True)

    def selectSubscriptionsWithTopic(self, topic):
        selectSub = '''SELECT * FROM subscriptions WHERE topic = ?'''
        # return the rows from the selection
        return self.execute_query_with_retry(query=selectSub, values=(topic,))

    def updateSubscriptionWithLatency(self, topic, new_lat_qos, new_max_lat):
        print(f"Topic: {topic}")
        print(f"Latency Req: {new_lat_qos}")
        print(f"Max Allowed Latency: {new_max_lat}")
        newSubQoS = (new_lat_qos, new_max_lat, topic)
        update_query = '''UPDATE subscriptions SET latency_req = ?, max_allowed_latency = ? WHERE topic = ?'''
        self.execute_query_with_retry(query=update_query, values=newSubQoS, requires_commit=True)

    




    
        
