import proto_db as db
import json

# A subscriber can subscribe to many topics with different latency qos
def updateDB(willMsg):
    update_values = list()
    print(f"Payload: {willMsg}")
    willMsg_json = json.loads(willMsg)
    # Extract Values
    clientid = willMsg_json["clientid"]
    print(clientid)
    topics_list = willMsg_json["topics"]
    print(type(topics_list))

    for i in range(len(topics_list)):
        # Remove %latency%
        latStringIndex = topics_list[i].rindex("%latency%")
        topics_list[i] = topics_list[i][:latStringIndex]

        print(topics_list[i])

        # Get rows from DB (array of tuple)
        impacted_sub = getImpactedSubscription(topics_list[i])
        impacted_sub = impacted_sub[0] # only 1 row, convert from array to single tuple 
        print(f"Old Latency Req: {impacted_sub}")
        # Convert latency_req to json
        latency_req_json = json.loads(impacted_sub[1])

        # Remove item with clientid key
        if(clientid in latency_req_json):
            print(f"Deleting client sub {clientid}")
            del latency_req_json[clientid]

        new_max_allowed = calculateNewMaxLatency(latency_req_json)
        
        # Convert back to string
        new_latency_req_str = json.dumps(latency_req_json)

        # Calculate new max_allowed_latency
        print(new_latency_req_str)


def getImpactedSubscription(topic) -> list:
    # get database
    database = db.Database()
    database.openDB()
    database.selectSubscriptionsWithTopic(topic)
    results = database._db_cursor.fetchall()
    return results

def calculateNewMaxLatency(latency_req_json):
    if not latency_req_json:
        return None
    for key in latency_req_json:
        print(key)
    pass

#Hash Map (topic: latency_req)

#List of tuples with the update values
    # [(newLatencyReq, newMax, willTopic), (newLatencyReq, newMax, willTopic), ...]
    # use executemany

# First: get the latency_req for a topic in the will_msg topics
    # SELECT * WHERE topic = willTopic
    # Convert the latency_req to a json object
    # remove their username from the latency_req object
    # Add to hash map (topic: dictionary latency_req)

# Second: Recalculate max_allowed_latency
    # For each key in the hash map
    # Loop over the keys in the latency_req dictionary, find the new max latency
    # Convert latency_req to string
    # Save willTopic, string latency_req, max_allowed_latency as a new tuple to the UpdateValues array of tuples

# Third: Update the DB
    # Convert the latency_req back to a string
    # UPDATE subscriptions SET latencyreq = ?, max_allowed_latency = ? WHERE topic = ?
    # values = ()


# Edge Cases:
    # Only 1 sub in a topic, when the subscriber disconnects, return an empty json string
        # set max_allowed_latency to NULL


