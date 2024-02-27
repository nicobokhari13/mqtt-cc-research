#ifndef MQTT_CC_H
#define MQTT_CC_H

#ifdef WITH_CJSON
#  include <cjson/cJSON.h>
#endif

#include <sqlite3.h>

struct mqttcc{
    char* incoming_topic; 
    int incoming_lat_qos;
    char* incoming_sub_clientid;
};

struct mqttcc_db{
    const char* db_path;
    sqlite3 *db;
    sqlite3_stmt *insert_new_topic; 
    sqlite3_stmt *update_latency_req; 
    sqlite3_stmt *find_existing_topic; 
};

#endif