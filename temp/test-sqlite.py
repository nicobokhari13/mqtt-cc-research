import sqlite3
import json
# # Connect to the SQLite database (creates a new one if it doesn't exist)
# conn = sqlite3.connect('example.db')

# # Create a cursor object to execute SQL commands
# cur = conn.cursor()

# # Create a table
# cur.execute('''CREATE TABLE IF NOT EXISTS devices (id TEXT PRIMARY KEY, battery FLOAT)''')

# # Insert some data into the table
# cur.execute('''INSERT INTO devices (id, battery) VALUES (?, ?)''', ('00-B0-D0-63-C2-26', 95.4))

# # Commit the transaction (save changes)
# conn.commit()

# # Query the data
# cur.execute('''SELECT * FROM devices''')
# rows = cur.fetchall()
# for row in rows:
#     print(row)

# # Close the cursor and the connection
# cur.close()
# conn.close()

# attribute in DB is TEXT
cars_string = '''["Ford", "BMW", "Fiat"]'''
print(cars_string)
print("_______")

# Load attribute into json object, which becomes a list
cars_json = json.loads(cars_string) 

print(type(cars_json))


for i in range(len(cars_json)):
    print(cars_json[i])

cars_json.pop(1)

print("_______")

print(cars_json)


