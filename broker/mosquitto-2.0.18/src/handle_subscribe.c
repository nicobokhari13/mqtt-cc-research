/*
Copyright (c) 2009-2020 Roger Light <roger@atchoo.org>

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

#include <stdio.h>
#include <string.h>

#include "mosquitto_broker_internal.h"
#include "memory_mosq.h"
#include "mqtt_protocol.h"
#include "packet_mosq.h"
#include "property_mosq.h"


int handle__subscribe(struct mosquitto *context)
{
	int rc = 0; // return code
	int rc2; // 2nd return code
	uint16_t mid; // message id
	char *sub;
	uint8_t subscription_options;
	uint32_t subscription_identifier = 0;
	uint8_t qos;
	uint8_t retain_handling = 0;
	uint8_t *payload = NULL, *tmp_payload;
	uint32_t payloadlen = 0;
	size_t len;
	uint16_t slen; 
	char *sub_mount; // if subscriptions were mounted to a specific port 
	mosquitto_property *properties = NULL;
	bool allowed;
	memset(&context->mqtt_cc, 0, sizeof(struct mqttcc));

	if(!context) return MOSQ_ERR_INVAL;

	if(context->state != mosq_cs_active){
		return MOSQ_ERR_PROTOCOL;
	}
	if(context->in_packet.command != (CMD_SUBSCRIBE|2)){
		return MOSQ_ERR_MALFORMED_PACKET;
	}

	log__printf(NULL, MOSQ_LOG_DEBUG, "Received SUBSCRIBE from %s", context->id);

	// checks for malformed packets against MQTT spec 3
	if(context->protocol != mosq_p_mqtt31){
		if((context->in_packet.command&0x0F) != 0x02){
			return MOSQ_ERR_MALFORMED_PACKET;
		}
	}
	
	// reads packet for message id 
	if(packet__read_uint16(&context->in_packet, &mid)) return MOSQ_ERR_MALFORMED_PACKET;
	if(mid == 0) return MOSQ_ERR_MALFORMED_PACKET;

	// tests for malformed packets against MQTT spec 5
	if(context->protocol == mosq_p_mqtt5){
		rc = property__read_all(CMD_SUBSCRIBE, &context->in_packet, &properties);
		if(rc){
			/* FIXME - it would be better if property__read_all() returned
			 * MOSQ_ERR_MALFORMED_PACKET, but this is would change the library
			 * return codes so needs doc changes as well. */
			if(rc == MOSQ_ERR_PROTOCOL){
				return MOSQ_ERR_MALFORMED_PACKET;
			}else{
				return rc;
			}
		}

		if(mosquitto_property_read_varint(properties, MQTT_PROP_SUBSCRIPTION_IDENTIFIER,
					&subscription_identifier, false)){

			/* If the identifier was force set to 0, this is an error */
			if(subscription_identifier == 0){
				mosquitto_property_free_all(&properties);
				return MOSQ_ERR_MALFORMED_PACKET;
			}
		}

		mosquitto_property_free_all(&properties);
		/* Note - User Property not handled */
	}

	// while the packet's position traverses the packet's length
	while(context->in_packet.pos < context->in_packet.remaining_length){
		sub = NULL;
		// check if subscription string follows UTF8 stirng standards 
		// characters like '%' are allowed and will return successfully from this packet read
		if(packet__read_string(&context->in_packet, &sub, &slen)){
			mosquitto__free(payload);
			return MOSQ_ERR_MALFORMED_PACKET;
		}
		if(sub){
			if(!slen){ // if the subscirption length is empty
				log__printf(NULL, MOSQ_LOG_INFO,
						"Empty subscription string from %s, disconnecting.",
						context->address);
				mosquitto__free(sub);
				mosquitto__free(payload);
				return MOSQ_ERR_MALFORMED_PACKET;
			}
			// check that the topic is valid according to wildcard rules
			if(mosquitto_sub_topic_check(sub)){ 
				log__printf(NULL, MOSQ_LOG_INFO,
						"Invalid subscription string from %s, disconnecting.",
						context->address);
				mosquitto__free(sub);
				mosquitto__free(payload);
				return MOSQ_ERR_MALFORMED_PACKET;
			}

			if(packet__read_byte(&context->in_packet, &subscription_options)){
				mosquitto__free(sub);
				mosquitto__free(payload);
				return MOSQ_ERR_MALFORMED_PACKET;
			}
			if(context->protocol == mosq_p_mqtt31 || context->protocol == mosq_p_mqtt311){
				qos = subscription_options;
				if(context->is_bridge){
					subscription_options = MQTT_SUB_OPT_RETAIN_AS_PUBLISHED | MQTT_SUB_OPT_NO_LOCAL;
				}
			}else{
				qos = subscription_options & 0x03;
				subscription_options &= 0xFC;

				retain_handling = (subscription_options & 0x30);
				if(retain_handling == 0x30 || (subscription_options & 0xC0) != 0){
					mosquitto__free(sub);
					mosquitto__free(payload);
					return MOSQ_ERR_MALFORMED_PACKET;
				}
			}
			if(qos > 2){
				log__printf(NULL, MOSQ_LOG_INFO,
						"Invalid QoS in subscription command from %s, disconnecting.",
						context->address);
				mosquitto__free(sub);
				mosquitto__free(payload);
				return MOSQ_ERR_MALFORMED_PACKET;
			}
			if(qos > context->max_qos){
				qos = context->max_qos;
			}

			// deals with subscription mounting on port listeners
			if(context->listener && context->listener->mount_point){
				len = strlen(context->listener->mount_point) + slen + 1;
				sub_mount = mosquitto__malloc(len+1);
				if(!sub_mount){
					mosquitto__free(sub);
					mosquitto__free(payload);
					return MOSQ_ERR_NOMEM;
				}
				snprintf(sub_mount, len, "%s%s", context->listener->mount_point, sub);
				sub_mount[len] = '\0';

				mosquitto__free(sub);
				sub = sub_mount;

			}
			log__printf(NULL, MOSQ_LOG_DEBUG, "\t%s (QoS %d)", sub, qos);
			// By this point, the subscribed topic is valid and ACL plugins are being evaluated
			allowed = true;
			rc2 = mosquitto_acl_check(context, sub, 0, NULL, qos, false, MOSQ_ACL_SUBSCRIBE);
			switch(rc2){  
				case MOSQ_ERR_SUCCESS: //since no ACL plugin is used, rc2 returns with SUCCESS
					break;
				case MOSQ_ERR_ACL_DENIED:
					allowed = false;
					if(context->protocol == mosq_p_mqtt5){
						qos = MQTT_RC_NOT_AUTHORIZED;
					}else if(context->protocol == mosq_p_mqtt311){
						qos = 0x80;
					}
					break;
				default:
					mosquitto__free(sub);
					return rc2;
			}
			if(allowed){// since the subscription topic is allowed
				if(has_lat_qos(sub)){ //check if it has %latency%*
					store_lat_qos(context, sub); // remove the lat qos from the sub
					if(!topic_exists_in_DB(context)){
						log__printf(NULL, MOSQ_LOG_DEBUG, "\ Topic does not exist in DB. Adding now");
						insert_topic_in_DB(context);
					}
					else{
						log__printf(NULL, MOSQ_LOG_DEBUG, "\ Topic already exists in DB");
					}
				}

				// add the subscription with sub__add in subs.c
				// the database (mosquitto_db in mosquitto_broker_internal.h) holds an array of mosquitto__subhiers
				// subhiers are all the subscriptions defined by '/' levels, and have a parent hiearchy + children hierarchies
				// subleafs are the specific subscriptions that exhibit a linked list structure (with prev and next) 
				rc2 = sub__add(context, sub, qos, subscription_identifier, subscription_options, &db.subs);
				if(rc2 > 0){
					mosquitto__free(sub);
					return rc2;
				}
				if(context->protocol == mosq_p_mqtt311 || context->protocol == mosq_p_mqtt31){
					if(rc2 == MOSQ_ERR_SUCCESS || rc2 == MOSQ_ERR_SUB_EXISTS){
						if(retain__queue(context, sub, qos, 0)) rc = 1;
					}
				}else{
					if((retain_handling == MQTT_SUB_OPT_SEND_RETAIN_ALWAYS)
							|| (rc2 == MOSQ_ERR_SUCCESS && retain_handling == MQTT_SUB_OPT_SEND_RETAIN_NEW)){

						if(retain__queue(context, sub, qos, subscription_identifier)) rc = 1;
					}
				}

				log__printf(NULL, MOSQ_LOG_SUBSCRIBE, "%s %d %s", context->id, qos, sub);
			}
			mosquitto__free(sub);

			tmp_payload = mosquitto__realloc(payload, payloadlen + 1);
			if(tmp_payload){


				payload = tmp_payload;
				payload[payloadlen] = qos;
				payloadlen++;
			}else{
				mosquitto__free(payload);

				return MOSQ_ERR_NOMEM;
			}
		}
	}

	if(context->protocol != mosq_p_mqtt31){
		if(payloadlen == 0){
			/* No subscriptions specified, protocol error. */
			return MOSQ_ERR_MALFORMED_PACKET;
		}
	}
	if(send__suback(context, mid, payloadlen, payload)) rc = 1;
	mosquitto__free(payload);

#ifdef WITH_PERSISTENCE
	db.persistence_changes++;
#endif

	if(context->current_out_packet == NULL){
		rc = db__message_write_queued_out(context);
		if(rc) return rc;
		rc = db__message_write_inflight_out_latest(context);
		if(rc) return rc;
	}

	return rc;
}


