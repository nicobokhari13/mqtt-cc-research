
topic_dict = {"topic/1":11, "topic/2":12, "topic/3":13,}

system_capability = {topic: (None, []) for topic in topic_dict.keys()}

print(system_capability)