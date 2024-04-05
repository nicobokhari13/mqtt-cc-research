import sqlite3
import time

class Database:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        self._db_path = "/home/devnico/repos/research/mqtt_cc_research/sqlite/mqttcc.db"

    def openDB(self) -> None:
        self._db_conn = sqlite3.connect(self._db_path)
        self._db_cursor = self._db_conn.cursor()

    def closeDB(self) -> None:
        self._db_cursor.close()
        self._db_conn.close()

    def execute_query_with_retry(self, query:str, values = None, requires_commit=False, max_retries=3, delay = 0.1, executeMany = False ):
        for i in range(max_retries):
            try: 
                cursor = self._db_conn.cursor()
                if values and executeMany:
                    cursor.executemany(query, values)
                elif values:
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
        self.execute_query_with_retry(query=deviceTable, requires_commit=True)

    def createPublishTable(self) -> None:
        publishSelectTable = '''
                                CREATE TABLE IF NOT EXISTS publish (
                                deviceMac TEXT, 
                                topic TEXT, 
                                publishing BOOLEAN,
                                FOREIGN KEY (deviceMac) REFERENCES devices(deviceMac),
                                FOREIGN KEY (topic) REFERENCES subscriptions(subscription) 
                                PRIMARY KEY (deviceMac, topic)
                                )'''
        # publish: True = is currently publishing to topic, False = is not currently publishing
        self.execute_query_with_retry(query=publishSelectTable, requires_commit=True)

    def selectSubscriptionsWithTopic(self, topic):
        selectSub = '''SELECT * FROM subscriptions WHERE subscription = ?'''
        # return the rows from the selection
        return self.execute_query_with_retry(query=selectSub, values=(topic,))

    def updateSubscriptionWithLatency(self, topic, new_lat_qos, new_max_lat):
        newSubQoS = (new_lat_qos, new_max_lat, topic)
        update_query = '''UPDATE subscriptions SET latency_req = ?, max_allowed_latency = ? WHERE subscription = ?'''
        self.execute_query_with_retry(query=update_query, values=newSubQoS, requires_commit=True)
        
    def topicsWithNoPublishers(self) -> list:
        selectQuery = '''SELECT DISTINCT topic, max_allowed_latency
                        FROM publish 
                        LEFT JOIN subscriptions
                        ON topic = subscription
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

    def devicePublishing(self, MAC_ADDR):
        selectQuery = '''SELECT topic, max_allowed_latency
                        FROM publish
                        LEFT JOIN subscriptions
                        ON subscription = topic
                        WHERE publishing = 1 AND deviceMac = ?'''
        deviceValue = (MAC_ADDR,)
        return self.execute_query_with_retry(query=selectQuery, values=deviceValue)
    
    def updateDeviceExecutions(self, MAC_ADDR, NEW_EXECUTIONS):
        updateQuery = '''UPDATE devices SET executions = ? WHERE deviceMac = ?'''
        device_values = (NEW_EXECUTIONS,MAC_ADDR)
        self.execute_query_with_retry(query=updateQuery, values=device_values, requires_commit=True)

    def updateDeviceStatus(self, MAC_ADDR, NEW_BATTERY):
        updateQuery = '''UPDATE devices SET battery = ? WHERE deviceMac = ?'''
        device_values = (NEW_BATTERY,MAC_ADDR)
        self.execute_query_with_retry(query=updateQuery, values=device_values, requires_commit=True)

    def updatePublishTableWithPublishingAssignments(self, MAC_ADDR, TOPICS):
        updateQuery = '''UPDATE publish SET publishing = 1 WHERE deviceMac = ? AND topic = ?'''
        update_values = []
        print(f"In update PUBLISH table: mac = {MAC_ADDR}")
        for topic in TOPICS:
            update_values.append((MAC_ADDR, topic))
        print(f"update_values: {update_values}")
        self.execute_query_with_retry(query=updateQuery, values=update_values, requires_commit=True, executeMany=True)

        
    def addDevice(self, MAC_ADDR, BATTERY):
        insertQuery = '''INSERT INTO devices (deviceMac, battery, executions) VALUES (?,?,?)'''
        device_values = (MAC_ADDR, BATTERY, 0)
        self.execute_query_with_retry(query=insertQuery, values=device_values, requires_commit=True)

    def addDeviceTopicCapability(self, MAC_ADDR, TOPIC):
        insertQuery = '''INSERT INTO publish (deviceMac, topic, publishing) VALUES (?,?,?)'''
        row_values = (MAC_ADDR, TOPIC, 0)
        self.execute_query_with_retry(query=insertQuery, values=row_values, requires_commit=True)

    def resetPublishings(self):
        updateQuery = '''UPDATE publish SET publishing = 0
                            WHERE topic IN (
                                SELECT subscription
                                FROM subscriptions);
                        '''
        self.execute_query_with_retry(query=updateQuery, requires_commit=True)

    def resetDeviceExecutions(self):
        updateQuery = '''UPDATE devices SET executions = 0'''
        self.execute_query_with_retry(query=updateQuery, requires_commit=True)

    def resetDevicesPublishingToTopic(self, changedTopic):
        updateQuery = '''UPDATE publish 
                            SET publishing = 0 
                            WHERE topic = ?'''
        query_values = (changedTopic,)
        self.execute_query_with_retry(query=updateQuery, values=query_values, requires_commit=True)
        
    def resetAllDevicesPublishing(self):
        updateQuery = '''UPDATE publish
                            SET publishing = 0'''
        self.execute_query_with_retry(query=updateQuery, requires_commit=True)