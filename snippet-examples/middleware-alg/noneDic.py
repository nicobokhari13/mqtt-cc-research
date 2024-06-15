import json
dict = {"None":"None"}
dict_string = json.dumps(dict)
print(dict_string)
dict_dict = json.loads(dict_string)
print(dict_dict)
if "None" in dict_dict.keys():
    print("empty command")

topic_list = [f"topic/{i}" for i in range(10)]
print(topic_list)
