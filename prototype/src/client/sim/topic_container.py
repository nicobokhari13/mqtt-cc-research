import random

class Topic_Container:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        self._total_topics = 0
        # possibly set some constants
        pass

    def setDefaultNumTopics(self, default_num_topics):
        self._default_num_topics = default_num_topics

    def setupTopicStrings(self, numTopics):
        if numTopics == 0:
            print(f"setting default topic {self._default_num_topic}")
            numTopics = self._default_num_topic
        self._total_topics = numTopics
        print(f"creating {numTopics} topics")
        self._topic_dict = dict()
        topic_list = self.generateTopics(numTopics)
        for topic in topic_list:
            self._topic_dict[topic] = -1 # default until changed

    def generateTopics(self, numTopics):
        topic_list = [f"topic/{i}" for i in range(numTopics)]
        print(topic_list)
        return topic_list
    
    def updateQoS(self, topic_changed, sub_lat):
        if self._topic_dict[topic_changed] < 0 or self._topic_dict[topic_changed] > sub_lat:
            self._topic_dict[topic_changed] = sub_lat
        else:
            print(f"max allowed latency for {topic_changed} wasn't changed")
    
    def unusedTopics(self):
        if -1 in self._topic_dict.values():
            return True
        else: 
            return False
        
    def clearTopicDict(self):
        self._topic_dict.clear()
    
    # Precondition: all topics are created, all subscribers created
        # all frequencies assigned to all topics
    # Postcondition: all_sense_timestamps is a dictionary where 
        # key: topic from topic_dict
        # value: list of frequency timestamps from 0 - T observation period 
        # this object will be the same across all algorithms, need deepcopy for each
        # only created once per round
    def setupSenseTimestamps(self):
        self._all_sense_timestamps = {}
        multiplier = 1
        timestamp_list = []
        for topic in self._topic_dict.keys():
            freq = self._topic_dict[topic]
            multiple  = freq * multiplier
            while multiple < 3600000:
                timestamp_list.append(multiple)
                multiplier+=1
                multiple  = freq * multiplier
            # at the end of the loop timestamp_list has all of freq's timestamps < T
            self._all_sense_timestamps[topic] = timestamp_list
            # example, if topic/1 publishes every 10ms, then topic/1: [10,20,30...]
            multiplier = 1
            timestamp_list.clear()   

    def resetSenseTimestamps(self):
        self._all_sense_timestamps.clear() 
    