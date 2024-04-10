import json
dict = {"None":"None"}
dict_string = json.dumps(dict)
print(dict_string)
dict_dict = json.loads(dict_string)
print(dict_dict)
if "None" in dict_dict.keys():
    print("empty command")
