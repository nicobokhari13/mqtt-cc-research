/*
Copyright (c) 2010-2019 Roger Light <roger@atchoo.org>

All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License 2.0
and Eclipse Distribution License v1.0 which accompany this distribution.

The Eclipse Public License is available at
   https://www.eclipse.org/legal/epl-2.0/
and the Eclipse Distribution License is available at
  http://www.eclipse.org/org/documents/edl-v10.php.

SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause

Contributors:
   Roger Light - initial implementation and documentation.
*/

#include "config.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "mosquitto_broker_internal.h"
#include "memory_mosq.h"
#include "mqtt_protocol.h"
#include "util_mosq.h"

#include "utlist.h"

// called by sub__topic_tokenise with the topic string and a pointer that was previously used, but saved to keep memory clean
static char *strtok_hier(char *str, char **saveptr)
{
	char *c;

	if(str != NULL){ // if the topic is not null
		*saveptr = str; // set the pointer to the topic's address
	}

	if(*saveptr == NULL){
		return NULL;
	}

	c = strchr(*saveptr, '/'); //get the firs tinstance of '/'
	if(c){
		str = *saveptr; 
		*saveptr = c+1;
		c[0] = '\0';
	}else if(*saveptr){
		/* No match, but surplus string */
		str = *saveptr;
		*saveptr = NULL;
	}
	return str;
}

// called when adding a subscription with sub__add() in subs.c 
// char *subtopic - the subscribed topic stirng
// char **local_sub - a pointer to the string local_sub
// char ***topics - the address of an array of strings called topics
// const char **sharename - the address to a string that is NULL 
int sub__topic_tokenise(const char *subtopic, char **local_sub, char ***topics, const char **sharename)
{	
	char *saveptr = NULL;
	char *token; 
	int count;
	int topic_index = 0;
	int i;
	size_t len;

	len = strlen(subtopic);
	if(len == 0){
		return MOSQ_ERR_INVAL;
	}
	//set local_sub's string value to the subscribed topic string
	*local_sub = mosquitto__strdup(subtopic); 
	if((*local_sub) == NULL) return MOSQ_ERR_NOMEM;

	count = 0;
	//saveptr is set to the local_sub's value, which currently holds the subscribed topic stirng
	saveptr = *local_sub; 
	// while saveptr is not a null terminator
	while(saveptr){ 
		// move saveptr to the first instance of '/' in the string that starts at the next character
		saveptr = strchr(&saveptr[1], '/'); 
		count++; // increment for each hierarchy
	} 
	// in MQTT 5.0 topic sharenames are allowed for load balancing
	*topics = mosquitto__calloc((size_t)(count+3) /* 3=$shared,sharename,NULL */, sizeof(char *));
	if((*topics) == NULL){
		mosquitto__free(*local_sub);
		return MOSQ_ERR_NOMEM;
	}
	if((*local_sub)[0] != '$'){
		(*topics)[topic_index] = ""; 
		topic_index++; 
	}
	// TODO: back here 
	token = strtok_hier((*local_sub), &saveptr);
	while(token){
		(*topics)[topic_index] = token;
		topic_index++;
		token = strtok_hier(NULL, &saveptr);
	}
	// if the topic is shared, continue with this, if not, return successfully
if(!strcmp((*topics)[0], "$share")){
		if(count < 2){
			mosquitto__free(*local_sub);
			mosquitto__free(*topics);
			return MOSQ_ERR_PROTOCOL;
		}

		if(sharename){
			(*sharename) = (*topics)[1];
		}

		for(i=1; i<count-1; i++){
			(*topics)[i] = (*topics)[i+1];
		}
		(*topics)[0] = "";
		(*topics)[count-1] = NULL;
	}
	return MOSQ_ERR_SUCCESS;
}
