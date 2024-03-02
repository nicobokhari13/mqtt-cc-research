
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
    const char *create_table_sql = "CREATE TABLE IF NOT EXISTS subscriptions (topic TEXT PRIMARY KEY, latency_req TEXT, max_allowed_latency INTEGER);";
    rc = sqlite3_exec(prototype_db.db, create_table_sql, 0, 0, &err_msg);
	log__printf(NULL, MOSQ_LOG_INFO, "Created Tables");

    if (rc != SQLITE_OK) {
        log__printf(NULL, MOSQ_LOG_ERR, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }
    // Statement Commands
    const char *find_existing_topic_cmd = "SELECT * FROM subscriptions WHERE topic = ?1";
    const char *insert_new_topic_cmd = "INSERT INTO subscriptions (topic, latency_req, max_allowed_latency) VALUES (?1, ?2, ?3)";
    const char *update_latency_req_max_allowed_cmd = "UPDATE subscriptions SET latency_req = ?1, max_allowed_latency = ?2 WHERE topic = ?3";

    // Prepare Statements

        // find existing topic statement
    rc = sqlite3_prepare_v2(prototype_db.db, find_existing_topic_cmd, -1, &prototype_db.find_existing_topic, 0);
    if (rc != SQLITE_OK) {
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to prepare statement 1: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1);
    }
        // insert new topic statement
    rc = sqlite3_prepare_v2(prototype_db.db, insert_new_topic_cmd, -1, &prototype_db.insert_new_topic, 0);
    if (rc != SQLITE_OK) {
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to prepare statement 2: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1);
    }
            // update latency req and max allowed latency statement
    rc = sqlite3_prepare_v2(prototype_db.db, update_latency_req_max_allowed_cmd, -1, &prototype_db.update_latency_req_max_allowed, 0);
    if (rc != SQLITE_OK) {
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to prepare statement 3: %s\n", sqlite3_errmsg(prototype_db.db));
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
        // RESET will be done in update_latency_req_max_allowed
        returnValue = true;
    }
    else if (rc != SQLITE_DONE){
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to execute statement: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1); // error in execution, leave program
    }
    else{ // since there is no row in the query, we can reset
        log__printf(NULL, MOSQ_LOG_ERR, "Could not find topic in DB\n");
        returnValue = false;
        rc2 = sqlite3_reset(prototype_db.find_existing_topic);
        if(rc2 != SQLITE_OK){ // 0 
            log__printf(NULL, MOSQ_LOG_ERR, "Failed to reset statement: %s\n", sqlite3_errmsg(prototype_db.db));
            exit(1);
        }
        log__printf(NULL, MOSQ_LOG_ERR, "Reset find_existing_topic\n");
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
    sqlite3_bind_int(prototype_db.insert_new_topic, 3, context->mqtt_cc.incoming_lat_qos);
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
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to reset insert_new_topic: %s\n", sqlite3_errmsg(prototype_db.db));
        exit(1);
    }
    log__printf(NULL, MOSQ_LOG_ERR, "Reset insert_new_topic\n");

    
    log__printf(NULL, MOSQ_LOG_DEBUG, "Success: Added topic, latency_req, and max_allowed_latency to DB\n");
    
}

int calc_new_max_latency(struct cJSON *latencies){

    int numLatencies = 0;
    cJSON *child = latencies->child;
    while(child != NULL){
        numLatencies++;
        child = child->next;
    }
    int *arr = (int *)malloc(numLatencies *sizeof(int));
    
    if (arr == NULL) {
        printf("Memory allocation failed\n");
        exit(1);
    }

    int i = 0;
    cJSON_ArrayForEach(child, latencies){
        log__printf(NULL, MOSQ_LOG_DEBUG, "Adding latency to int array %ds\n", child->valueint);
        arr[i] = child->valueint;
        i++; 
    }
    int min = arr[0];
    for(i = 1; i < numLatencies; i++){
        if(arr[i] < min){
            min = arr[i];
        }
    }

    return min;
}


void update_lat_req_max_allowed(struct mosquitto *context){
    // at this point, the topic does exist in the DB, and the find_existing_topic stmt contains the row
    int rc;
    // get the old latency value from column 1 (latencyReq)
    
    char *oldLatencyValue = sqlite3_column_text(prototype_db.find_existing_topic, 1);
    
    log__printf(NULL, MOSQ_LOG_DEBUG, "old Latency Value: %s\n", oldLatencyValue);

    // convert old latency value to json
    cJSON *db_Value = cJSON_Parse(oldLatencyValue);
    // error checking db_Value
    if (db_Value == NULL) { 
        const char *error_ptr = cJSON_GetErrorPtr(); 
    if (error_ptr != NULL) { 
        log__printf(NULL, MOSQ_LOG_DEBUG, "Error: %s\n", error_ptr);
    } 
        log__printf(NULL, MOSQ_LOG_DEBUG, "Exiting Program with db_Value == NULL \n");
        cJSON_Delete(db_Value); 
        exit(1); 
    }
    log__printf(NULL, MOSQ_LOG_DEBUG, "Adding clientid %s and latQos %d to topic %s \n", context->mqtt_cc.incoming_sub_clientid, context->mqtt_cc.incoming_lat_qos, context->mqtt_cc.incoming_topic);


    // calculate the new max allowed latency from 
    // context->mqtt_cc.incoming_lat_qos + the row's existing latencies

    // add new item (clientid: latencyNum) to make new latency value
    cJSON_AddNumberToObject(db_Value, context->mqtt_cc.incoming_sub_clientid, context->mqtt_cc.incoming_lat_qos);

    int newMaxAllowed = calc_new_max_latency(db_Value);

    // convert new latency value back into string
    char *newLatencyValue = cJSON_Print(db_Value);
    
    log__printf(NULL, MOSQ_LOG_DEBUG, "new Latency Value: %s\n", newLatencyValue);
    log__printf(NULL, MOSQ_LOG_DEBUG, "new max allowed latency: %d\n", newMaxAllowed);

    // bind topic and new latency value to update statement

    sqlite3_bind_text(prototype_db.update_latency_req_max_allowed, 1, newLatencyValue, -1, SQLITE_STATIC);
    sqlite3_bind_int(prototype_db.update_latency_req_max_allowed, 2, newMaxAllowed);
    sqlite3_bind_text(prototype_db.update_latency_req_max_allowed, 3, context->mqtt_cc.incoming_topic, -1, SQLITE_STATIC);
    
    // step update statement    
    rc = sqlite3_step(prototype_db.update_latency_req_max_allowed);

    // check if statement is DONE
    if (rc != SQLITE_DONE) {
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to execute statement: %s\n", sqlite3_errmsg(prototype_db.db));
        sqlite3_close(prototype_db.db);
        exit(1);
    }

    log__printf(NULL, MOSQ_LOG_DEBUG, "Success: Added Latency Req %d to topic %s for client %s\n", context->mqtt_cc.incoming_lat_qos, context->mqtt_cc.incoming_topic, context->mqtt_cc.incoming_sub_clientid);

        // reset update stmt

    rc = sqlite3_reset(prototype_db.update_latency_req_max_allowed);
    

    // check if reset update stmt was good
    if(rc != SQLITE_OK){
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to reset update statement: %s\n", sqlite3_errmsg(prototype_db.db));
        exit(1);
    }

    log__printf(NULL, MOSQ_LOG_ERR, "Reset update_latency_req_max_allowed after \n");

    // reset find stmt 

    rc = sqlite3_reset(prototype_db.find_existing_topic);

    // check if reset find stmt was good 
    if(rc != SQLITE_OK){
        log__printf(NULL, MOSQ_LOG_ERR, "Failed to reset find statement: %s\n", sqlite3_errmsg(prototype_db.db));
        exit(1);
    }

    log__printf(NULL, MOSQ_LOG_ERR, "Reset find_existing_topic\n");
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





    