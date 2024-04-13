import sys
import csv
import subprocess

def main():
    subsfilename = sys.argv[1]
    pidfilename = "sub_pidfile.txt"
    try: 
        with open(subsfilename, 'r', newline='') as subfile:
            reader = csv.reader(subfile)
            rows = list(reader)
    except FileNotFoundError:
        print("File not found ", subsfilename)
        sys.exit()
    command = []
    for i in range(len(rows)):
        username = rows[i][0]
        topicList = rows[i][1:len(rows[i])] # rest of rows are the topics
        topicString = ','.join(topicList)
        # append subscriber's command to commands list
        print(username)
        command.append(["python3", "subscriber.py", username, topicString, "&"])
    with open(pidfilename, "a") as file: 
        for sub in command: 
            print(sub)
            try:
                process = subprocess.Popen(sub, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                pid = process.pid
                file.write(str(pid) + "\n")
            except subprocess.CalledProcessError as e:
                print(f"Error with running {sub}: {e}")



if __name__ == "__main__":
    main()

