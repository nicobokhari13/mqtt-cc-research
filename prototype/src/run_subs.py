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
        password = rows[i][1]
        topicList = rows[i][2:len(rows[i])] # rest of rows are the topics
        topicString = ','.join(topicList)
        # append subscriber's command to commands list
        command.append(["python3", "subscriber.py", username, password, topicString, "&"])
    with open(pidfilename, "a") as file: 
        for sub in command: 
            print(sub)
            try:
                # TODO: Get pids from these processes and save them to a file
                    # each pid is on a new line
                    # create a bash script that reads this file and kills the subscribers
                    # to fast track testing
                process = subprocess.Popen(sub, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                pid = process.pid
                file.write(str(pid) + "\n")
            except subprocess.CalledProcessError as e:
                print(f"Error with running {sub}: {e}")



if __name__ == "__main__":
    main()

