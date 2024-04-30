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

    def setTopicStrings(self, numTopics):
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
        
    def ensureTopicCoverage(self):
        for topic in self._topic_dict.keys():
            if self._topic_dict[topic] < -1:
                self._topic_dict[topic] = random.randrange(start=100, stop=10001)
            
    
    
    
    
