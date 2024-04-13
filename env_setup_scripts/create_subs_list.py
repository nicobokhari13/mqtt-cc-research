import random
import string
import csv

def generateSubscriberNames(numSubs):
    sub_names= []
    for i in range(numSubs):
        name = f"sub00{i}"
        sub_names.append(name)
    print(sub_names)
    return sub_names

def createSubscriberCSV(sub_rows):
    filePath = "./subscribers.csv"
    lines = []
    with open(filePath, 'w', newline='') as file:
        for row in sub_rows: 
            line = f"{row}"
            lines.append(line)
        for row in lines:
            file.write(row + "\n")


def generateSubscriptions(sub_name, topic_list, latency_range):
    row = [sub_name]
    subscriptions = []
    unique_random_indices = set()
    latency_min = 0
    latency_max = 0
    num_subscription = random.randint(1, len(topic_list)) # subscribe to 1 or all the topics

    while len(unique_random_indices) < num_subscription:
        unique_random_indices.add(random.randrange(0, len(topic_list))) # choose an index between 0 and len(topic_list) - 1 
    for index in unique_random_indices:
        subscriptions.append(topic_list[index]) # append the topic to the row
    
    if latency_range: 
        if latency_range == 50:
            latency_min = 5
            latency_max = 55
        elif latency_range == 40:
            latency_min = 10
            latency_max = 50
        elif latency_range == 35:
            latency_min = 15
            latency_max = 45
        elif latency_range == 30:
            latency_min = 20
            latency_max = 40
        elif latency_range == 20:
            latency_min = 25
            latency_max = 35

        for i in range(len(subscriptions)):
            random_latency = random.randint(latency_min, latency_max)
            subscriptions[i] = f"{subscriptions[i]}%latency%{random_latency}"
    
    subscription_string = ""
    for sub in subscriptions:
        subscription_string = subscription_string + sub + ","
    
    if subscription_string[len(subscription_string) - 1] == ",":
        subscription_string = subscription_string[:-1]

    sub_row = f"{sub_name},{subscription_string}"
    print(sub_row)
    return sub_row
        


