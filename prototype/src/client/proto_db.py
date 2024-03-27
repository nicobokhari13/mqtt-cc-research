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
                                deviceMac TEXT PRIMARY KEY, 
                                battery FLOAT, 
                                executions INTEGER)'''
        # TODO: query to update number of executions a device is making after cmd is created
        self.execute_query_with_retry(query=deviceTable, requires_commit=True)

    def createPublishTable(self) -> None:
        publishSelectTable = '''
                                CREATE TABLE IF NOT EXISTS publish (
                                deviceMac TEXT, 
                                topic TEXT, 
                                capability BOOLEAN,
                                publish BOOLEAN,
                                FOREIGN KEY (deviceMac) REFERENCES devices(deviceMac),
                                FOREIGN KEY (topic) REFERENCES subscriptions(topic) 
                                PRIMARY KEY (deviceMac, topic)
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

    
    # TODO: Queries for algorithm
        
    def topicsWithNoPublishers(self) -> list:
        selectQuery = '''SELECT DISTINCT topic, max_allowed_latency
                        FROM publish 
                        LEFT JOIN subscriptions
                        ON subscription = topic
                        WHERE NOT EXISTS  (
                            SELECT 1
                            FROM publish
                            WHERE topic = subscription
                            AND publishing = 1
                        )'''
        return self.execute_query_with_retry(query=selectQuery)

    def devicesCapableToPublish(self, topicName):
        selectQuery = '''SELECT devices.deviceMac, battery, executions
                        FROM devices
                        LEFT JOIN publish
                        ON devices.deviceMac = publish.deviceMac
                        WHERE topic = ?'''
        topicValue = (topicName,)
        return self.execute_query_with_retry(query=selectQuery, values=topicValue)

    def deviceTopicCapability(self, MAC_ADDR):
        selectQuery = '''SELECT topic, max_allowed_latency
                        FROM publish
                        LEFT JOIN subscriptions
                        ON subscription = topic
                        WHERE publishing = 1 AND deviceMac = ?'''
        deviceValue = (MAC_ADDR,)
        return self.execute_query_with_retry(query=selectQuery, values=deviceValue)
    
    # TODO: Queries to update device table after status
        
    # TODO: Query to add device topic capability from device txt (DB can be prepared before simulation)
        



    
        
