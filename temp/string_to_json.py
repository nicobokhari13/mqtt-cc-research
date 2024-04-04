import json

# Create a dictionary to represent your data
data = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# Convert the dictionary to a JSON string
json_string = json.dumps(data)

# Print the JSON string
print("JSON String:", json_string)

# Convert the JSON string back to a regular Python string
decoded_data = json.loads(json_string)

# Print the decoded data
print("Decoded Data:", decoded_data) 
