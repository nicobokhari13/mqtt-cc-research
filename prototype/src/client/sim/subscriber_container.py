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
        self._default_num_subs = 8
        pass

    def setUpLatQoS(self, num_subs):
        if num_subs == 0:
            print(f"setting default subscribers {self._default_num_subs}")
            num_subs = self._default_num_subs
        print(f"creating {num_subs} subscribers")
        topics = Topic_Container()
        for sub in range(num_subs):
            num_subscriptions = random.randrange(start=1, stop=topics._total_topics + 1)
            subscriptions = random.sample(population=topics._topic_dict.keys(), k=num_subscriptions)
            for subscription in subscriptions:
                sub_lat_qos = random.randomrange(start=100, stop=10001)
                topics.updateQoS(topic_changed=subscription, sub_lat=sub_lat_qos)
            
