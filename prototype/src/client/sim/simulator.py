from constants import ConfigUtils
from datetime import datetime
from subscriber_container import Subscriber_Container
from pub_container import Publisher_Container
from topic_container import Topic_Container

configuration = ConfigUtils()
configuration.setConstants("config.ini")
file_paths = {
    "pub_path": "../results_pubs/",
    "sub_path": "../results_subs/",
    "topic_path": "../results_topics/"
}
filename = "results_" + datetime.now() + "_"

def saveResults(energy_consumption:float, algo_name:str):
    if configuration._vary_pubs:
        filename = file_paths["pub_path"] + filename + algo_name
    elif configuration._vary_subs:
        filename = file_paths["sub_path"] + filename + algo_name
    elif configuration._vary_topics:
        filename = file_paths["topic_path"] + filename + algo_name


def main():
    pass 
# based on which variable that varies, store round results in different files
    # filename = "results" + datetime.now
    # if var_pubs -> filename += "pubs"
    # elif var_subs -> filename += "subs"
    # elif var_topics -> filename += "topics"

# print to a csv requires
    # filename, data

# saveResults(energy_consumption, algorithm)
    # if configuration._vary_pubs
        # filename = file_paths["pub_path"] + filename + algorithm


