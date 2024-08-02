import sys
import csv
import subprocess

def main():
    pubsfilename = sys.argv[1]

#    pubsfilename = "devices.csv"
    pidfilename = "pub_pidfile.txt"
    try: 
        with open(pubsfilename, 'r', newline='') as pubfile:
            reader = csv.reader(pubfile)
            rows = list(reader)
    except FileNotFoundError:
        print("File not found ", pubsfilename)
        sys.exit()
    command = []
    for i in range(len(rows)):
        exp_type = rows[i][0]
        username = rows[i][1]
        battery = rows[i][2]
        energy = rows[i][3]
        freq_range = rows[i][4]
        topicList = rows[i][5:len(rows[i])] # rest of rows are the topics
        topicString = ','.join(topicList)
        # append subscriber's command to commands list
        print(username)
        command.append(["python3", "sensor.py", exp_type, username, battery, energy, freq_range, topicString, "&"])
    with open(pidfilename, "a") as file: 
        for sub in command: 
            print(sub)
            try:
                process = subprocess.Popen(sub, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                pid = process.pid
                file.write(str(pid) + "\n")
            except subprocess.CalledProcessError as e:
                print(f"Error with running {sub}: {e}")

    while True:
        print("running pubs")

if __name__ == "__main__":
    main()

