
def createTopicList(num_topics):
    topic_list = [f"topic/{i}" for i in range(num_topics)]
    print(topic_list)
    return topic_list

def createClientScript(exp_type, algo_window, energy, threshold):
    # devicePath sim 900 0.3 3
    filePath = "./run_prototype.sh"
    lines = [
        "#!/bin/bash", 
        "if [ $# -eq 0 ]; then", 
        "exit 1", 
        "fi", 
        "file_path = $1", 
        'if [ ! -f "$file_path" ]; then', 
        "exit 1", 
        "fi",
        ]
    with open(filePath, 'w', newline='') as file:
        for row in lines:
            file.write(row + "\n")
        line = f'python3 proto_client.py "$file_path" {exp_type} {algo_window} {energy} {threshold}'
        file.write(line + "\n")
