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
        self._db_conn.close()

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
        
    




    
        
