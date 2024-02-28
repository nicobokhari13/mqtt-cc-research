
#include "config.h"

#include <string.h>

#include "mosquitto_broker_internal.h"



void log_sub(char *sub){
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t %s", sub);
}

bool has_lat_qos(char *sub){
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t in has_lat_qos");
    char *latencyStr = "%latency%";
    char* result = strstr(sub, latencyStr);
    if(result == NULL){
        log__printf(NULL, MOSQ_LOG_DEBUG, "\t in has_lat_qos if statement");
        return false;
    }
    return true;
}

void printStmtResults(sqlite3_stmt *stmt){
    int rc;
    int i; 
    int columnNum = sqlite3_column_count(stmt);
    for (i = 0; i < columnNum; i++){
            log__printf(NULL, MOSQ_LOG_DEBUG, "%s = %s \n", sqlite3_column_name(stmt, i), sqlite3_column_text(stmt,i));
    }
    while((rc = sqlite3_step(stmt)) == SQLITE_ROW){
        int columnNum = sqlite3_column_count(stmt);
        for (i = 0; i < columnNum; i++){
            log__printf(NULL, MOSQ_LOG_DEBUG, "%s = %s \n", sqlite3_column_name(stmt, i), sqlite3_column_text(stmt,i));
        }
        log__printf(NULL, MOSQ_LOG_DEBUG, "\n");
    }
}

// Need full mosquitto context to extract clientid of the subscriber that send incoming_sub
void store_lat_qos(struct mosquitto *context, char* sub_with_lat_qos){
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t in store_lat_qos");
    char *latencyStr = "%latency%";
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t before strstr");
    char* result = strstr(sub_with_lat_qos, latencyStr); // result points at %latenct%* in sub_with_lat_qos
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t after strstr");
    size_t latStr_len = strlen(result); 
    //allocate the necessary memory for holding just the latency in context
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t before allcoating mem to temp_lat_qos");
    char* temp_lat_qos = malloc(latStr_len - 7);
    
    strcpy(temp_lat_qos, result + 9); // ignores the %latency% substring, keeps the numbers afterward
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t after strcpy");
    context->mqtt_cc.incoming_lat_qos = atoi(temp_lat_qos);
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t Latency QoS: %d", context->mqtt_cc.incoming_lat_qos);
    // remove the latency qos from the subscription
    while(*result){
            *result = *(result + latStr_len);
            result++;
    }
    // save the sub, which no longer has the latency qos attached
    context->mqtt_cc.incoming_topic = sub_with_lat_qos; 
    context->mqtt_cc.incoming_sub_clientid = context->id;
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t For Topic: %s", context->mqtt_cc.incoming_topic);
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t For Subscriber: %s", context->mqtt_cc.incoming_sub_clientid);
}

void prepare_DB(){
	log__printf(NULL, MOSQ_LOG_INFO, "in prepare DB");

    prototype_db.db_path = "/home/devnico/repos/research/sqlite/mqttcc.db";
	log__printf(NULL, MOSQ_LOG_INFO, "after set db_path");


    // Open the Database
    char *err_msg = 0;
    int rc = sqlite3_open(prototype_db.db_path, &prototype_db.db);
	log__printf(NULL, MOSQ_LOG_INFO, "opened DB");

    if (rc != SQLITE_OK){
        log__printf(NULL, MOSQ_LOG_ERR, "Cannot open database: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1);
    }

    // Create Tables
    const char *create_table_sql = "CREATE TABLE IF NOT EXISTS subscriptions (topic TEXT PRIMARY KEY, latencyReq TEXT);";
    rc = sqlite3_exec(prototype_db.db, create_table_sql, 0, 0, &err_msg);
	log__printf(NULL, MOSQ_LOG_INFO, "Created Tables");

    if (rc != SQLITE_OK) {
        log__printf(NULL, MOSQ_LOG_ERR, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }
    // Statement Commands
    const char *find_existing_topic_cmd = "SELECT * FROM subscriptions WHERE topic = ?1";
    const char *insert_new_topic_cmd = "INSERT INTO subscriptions (topic, latencyReq) VALUES (?1, ?2)";
    const char *update_latency_req_cmd = "UPDATE subscriptions SET latencyReq = ?1 WHERE topic = ?2";

    // Prepare Statements

        // find existing topic statement
    rc = sqlite3_prepare_v2(prototype_db.db, find_existing_topic_cmd, -1, &prototype_db.find_existing_topic, 0);
    if (rc != SQLITE_OK) {
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to prepare statement: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1);
    }
        // insert new topic statement
    rc = sqlite3_prepare_v2(prototype_db.db, insert_new_topic_cmd, -1, &prototype_db.insert_new_topic, 0);
    if (rc != SQLITE_OK) {
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to prepare statement: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1);
    }
            // update latency statement
    rc = sqlite3_prepare_v2(prototype_db.db, update_latency_req_cmd, -1, &prototype_db.update_latency_req, 0);
    if (rc != SQLITE_OK) {
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to prepare statement: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1);
    }


    log__printf(NULL, MOSQ_LOG_DEBUG, "Success: Prepared Statements\n");

} // (called in mosquitto.c's main )

bool topic_exists_in_DB(struct mosquitto *context){
    int rc;
    int rc2;
    bool returnValue;
    // bind incoming_topic to find_existing_topic sql statement
    log__printf(NULL, MOSQ_LOG_ERR, "Binding %s to find topic in DB \n", context->mqtt_cc.incoming_topic);
    sqlite3_bind_text(prototype_db.find_existing_topic, 1, (const char*)context->mqtt_cc.incoming_topic, -1, SQLITE_STATIC);
    // execute the statement
    rc = sqlite3_step(prototype_db.find_existing_topic);
    log__printf(NULL, MOSQ_LOG_ERR, "return code: %d \n", rc);
    if(rc == SQLITE_ROW){ // 100
        //printStmtResults(prototype_db.find_existing_topic);
        //rc2 = sqlite3_reset(prototype_db.find_existing_topic);
        // DO NOT RESET, since there is a row in the find_existing_topic statement
        // RESET will be done in update_latency_req
        returnValue = true;
    }
    else if (rc != SQLITE_DONE){
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to execute statement: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1); // error in execution, leave program
    }
    else{ // since there is no row in the query, we can reset
        log__printf(NULL, MOSQ_LOG_ERR, "Could not find topic in DB\n");
        rc2 = sqlite3_reset(prototype_db.find_existing_topic);
        if(rc2 != SQLITE_OK){ // 0 
            log__printf(NULL, MOSQ_LOG_ERR, "Failed to reset statement: %s\n", sqlite3_errmsg(prototype_db.db));
            exit(1);
        }
        returnValue = false;
    }


    return returnValue;

}

char* create_latency_str(char *clientid, int latencyNum){
    cJSON *json = cJSON_CreateObject();
    cJSON_AddNumberToObject(json, clientid, latencyNum);
    return cJSON_Print(json);
}

void insert_topic_in_DB(struct mosquitto *context){
    int rc;
    int rc2; 
    // create latency column value
    char *latencyJsonString = create_latency_str(context->mqtt_cc.incoming_sub_clientid, context->mqtt_cc.incoming_lat_qos);

    //bind topic and latency to prepared statement 
    sqlite3_bind_text(prototype_db.insert_new_topic, 1, context->mqtt_cc.incoming_topic, -1, SQLITE_STATIC);
    sqlite3_bind_text(prototype_db.insert_new_topic, 2, latencyJsonString, -1, SQLITE_STATIC);
    
    //execute statement
    rc = sqlite3_step(prototype_db.insert_new_topic);

    //check for error 
    if (rc != SQLITE_DONE) {
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to execute statement: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1);
    }

    rc2 = sqlite3_reset(prototype_db.insert_new_topic);
    if(rc2 != SQLITE_OK){
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to reset statement: %s\n", sqlite3_errmsg(prototype_db.db));
        exit(1);
    }
    
    log__printf(NULL, MOSQ_LOG_DEBUG, "Success: Added topic and latency to DB\n");
    
}

void update_lat_req(struct mosquitto *context){
    // at this point, the topic does exist in the DB, and the find_existing_topic stmt contains the row
    
    // get the old latency value

    // convert old latency value to json

    // add new item (clientid: latencyNum) to make new latency value

    // convert new latency value back into string

    // bind topic and new latency value to update statement

    // step update statement

    // check if statement is DONE

    // reset update stmt

    // check if reset update stmt was good

    // reset find stmt 

    // check if reset find stmt was good 
}



// TODO: Research Meeting Notes 2/14
// Functions: 
 // add sub to SQLite DB

 // Prototype

    // publishers (Iot Devices) publish battery, frequency to /status topic
        // plugins can customize callbacks for when a message is published to "$CONTROL/<feature>"
        //MOSQ_CONTROL_EVT
    
    // Quick-Dirty -> client
        // C++ < Python
        // use standard client
        // using standard mosquitto msgs
        // focuses on implementation logic with DB
        // client is a script running on the broker
        // when the broker starts, it starts up the client
    

    // Mosquitto "Correct Way" -> modifies the broker

    // Subscribers
        // sensor/temp
        //sub 01 sensor/temp%latency%10ms
            //sub 02 sensor/temp%latency%20ms 
            //sub 03 sensor/temp%latency%30ms

    // Experiment Design (Real World test bed)
        // Broker on Desktop
            // monitor Desktop for performance
            // Client monitors IoT devices status and all sensor reading updates
            // assume linear-rel between sample-freq + latency

        // 2-3 Raspberry Pis (IoT Devices)
            // need battery packs
            // in possession, come to Song/Li for sensors + Pis (after Spring Break)

        // Subscribers (on different device, probably desktop)

        // derive some topics for subscribers





    