
#include "config.h"

#include <string.h>
#include "mosquitto_broker_internal.h"

void log_sub(char *sub){
    log__printf(NULL, MOSQ_LOG_DEBUG, "\t %s", sub);
}

//PRECONDITION: sub is a utf8 string that is a valid topic name
bool check_sub_lat_param(char *sub){
    char *latencyStr = "%latency%";
    size_t latStr_len = strlen(latencyStr);
    char* result = strstr(sub, latencyStr);
    if(result == NULL){
        return false;
    }
    else{// the string %latency% exists in sub
        // remove it from the string
        while(*result){
            *result = *(result + latStr_len);
            result++;
        }
        // sub: /test/topic%latency%
        // after sub: /test/topic
        return true;
    }
}

// TODO: 
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





    