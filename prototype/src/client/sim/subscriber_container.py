import random
from topic_container import Topic_Container

class Subscriber_Container:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        # possibly set some constants
        self._total_subs = 0
        pass

    def setDefaultNumSubs(self, default_num_subs):
        self._default_num_subs = default_num_subs

    def setLatencyMinMax(self, min, max):
        self._lat_qos_min = min
        self._lat_qos_max = max

    # Precondition: Topics in Topic Container are created beforehand, defaults are set
    def setUpLatQoS(self, num_subs):
        if num_subs == 0:
            print(f"setting default subscribers {self._default_num_subs}")
            num_subs = self._default_num_subs
        self._total_subs = num_subs
        print(f"creating {num_subs} subscribers")
        topics = Topic_Container()
        for sub in range(num_subs):
            num_subscriptions = random.randint(start=1, stop=topics._total_topics)
            subscriptions = random.sample(population=topics._topic_dict.keys(), k=num_subscriptions)
            for subscription in subscriptions:
                sub_lat_qos = random.randomint(a=self._lat_qos_min, b=self._lat_qos_max)
                topics.updateQoS(topic_changed=subscription, sub_lat=sub_lat_qos)

    def ensureTopicCoverage(self):
        topics = Topic_Container()
        for topic in topics._topic_dict.keys():
            if topics._topic_dict[topic] < -1:
                topics._topic_dict[topic] = random.randint(a=self._lat_qos_min, b=self._lat_qos_max)
