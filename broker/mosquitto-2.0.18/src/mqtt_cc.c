
#include "config.h"

#include <string.h>

#include "mosquitto_broker_internal.h"

void log_sub(char *sub){
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t %s", sub);
}

bool has_lat_qos(char *sub){
    char *latencyStr = "%latency%";
    char* result = strstr(sub, latencyStr);
    if(result == NULL){
        return false;
    }
    return true;
}
// note that the subscriber's clientid is stored in context->id
// important for tracking latencies as subscribers disconnect

// may need to use atoi to convert string numbers to actual integers to store in sqlite DB
void store_lat_qos(struct mosquitto *context, char* sub_with_lat_qos){
    char *latencyStr = "%latency%";
    char* result = strstr(sub_with_lat_qos, latencyStr); // result points at %latenct%* in sub_with_lat_qos
    size_t latStr_len = strlen(result); 
    //allocate the necessary memory for holding just the latency in context
    char* temp_lat_qos = malloc(latStr_len - 7);
    strcpy(temp_lat_qos, result + 9); // ignores the %latency% substring, keeps the numbers afterward
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





    