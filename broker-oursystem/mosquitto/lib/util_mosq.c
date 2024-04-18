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

#include <assert.h>
#include <ctype.h>
#include <string.h>

#ifdef WIN32
#  include <winsock2.h>
#  include <aclapi.h>
#  include <io.h>
#  include <lmcons.h>
#else
#  include <sys/stat.h>
#endif

#if !defined(WITH_TLS) && defined(__linux__) && defined(__GLIBC__)
#  if __GLIBC_PREREQ(2, 25)
#    include <sys/random.h>
#    define HAVE_GETRANDOM 1
#  endif
#endif

#ifdef WITH_TLS
#  include <openssl/bn.h>
#  include <openssl/rand.h>
#endif

#ifdef WITH_BROKER
#include "mosquitto_broker_internal.h"
#endif

#include "mosquitto.h"
#include "memory_mosq.h"
#include "net_mosq.h"
#include "send_mosq.h"
#include "time_mosq.h"
#include "tls_mosq.h"
#include "util_mosq.h"

#ifdef WITH_WEBSOCKETS
#include <libwebsockets.h>
#endif

int mosquitto__check_keepalive(struct mosquitto *mosq)
{
	time_t next_msg_out;
	time_t last_msg_in;
	time_t now;
#ifndef WITH_BROKER
	int rc;
#endif
	enum mosquitto_client_state state;

	assert(mosq);
#ifdef WITH_BROKER
	now = db.now_s;
#else
	now = mosquitto_time();
#endif

#if defined(WITH_BROKER) && defined(WITH_BRIDGE)
	/* Check if a lazy bridge should be timed out due to idle. */
	if(mosq->bridge && mosq->bridge->start_type == bst_lazy
				&& mosq->sock != INVALID_SOCKET
				&& now - mosq->next_msg_out - mosq->keepalive >= mosq->bridge->idle_timeout){

		log__printf(NULL, MOSQ_LOG_NOTICE, "Bridge connection %s has exceeded idle timeout, disconnecting.", mosq->id);
		net__socket_close(mosq);
		return MOSQ_ERR_SUCCESS;
	}
#endif
#ifdef WITH_THREADING
	pthread_mutex_lock(&mosq->msgtime_mutex);
#endif
	next_msg_out = mosq->next_msg_out;
	last_msg_in = mosq->last_msg_in;
#ifdef WITH_THREADING
	pthread_mutex_unlock(&mosq->msgtime_mutex);
#endif
	if(mosq->keepalive && mosq->sock != INVALID_SOCKET &&
			(now >= next_msg_out || now - last_msg_in >= mosq->keepalive)){

		state = mosquitto__get_state(mosq);
		if(state == mosq_cs_active && mosq->ping_t == 0){
			send__pingreq(mosq);
			/* Reset last msg times to give the server time to send a pingresp */
#ifdef WITH_THREADING
			pthread_mutex_lock(&mosq->msgtime_mutex);
#endif			
			mosq->last_msg_in = now;
			mosq->next_msg_out = now + mosq->keepalive;
#ifdef WITH_THREADING
			pthread_mutex_unlock(&mosq->msgtime_mutex);
#endif			
		}else{
#ifdef WITH_BROKER
#  ifdef WITH_BRIDGE
			if(mosq->bridge){
				context__send_will(mosq);
			}
#  endif
			net__socket_close(mosq);
#else
			net__socket_close(mosq);
			state = mosquitto__get_state(mosq);
			if(state == mosq_cs_disconnecting){
				rc = MOSQ_ERR_SUCCESS;
			}else{
				rc = MOSQ_ERR_KEEPALIVE;
			}
#ifdef WITH_THREADING
			pthread_mutex_lock(&mosq->callback_mutex);
#endif			
			if(mosq->on_disconnect){
				mosq->in_callback = true;
				mosq->on_disconnect(mosq, mosq->userdata, rc);
				mosq->in_callback = false;
			}
			if(mosq->on_disconnect_v5){
				mosq->in_callback = true;
				mosq->on_disconnect_v5(mosq, mosq->userdata, rc, NULL);
				mosq->in_callback = false;
			}
#ifdef WITH_THREADING			
			pthread_mutex_unlock(&mosq->callback_mutex);
#endif			

			return rc;
#endif
		}
	}
	return MOSQ_ERR_SUCCESS;
}

uint16_t mosquitto__mid_generate(struct mosquitto *mosq)
{
	/* FIXME - this would be better with atomic increment, but this is safer
	 * for now for a bug fix release.
	 *
	 * If this is changed to use atomic increment, callers of this function
	 * will have to be aware that they may receive a 0 result, which may not be
	 * used as a mid.
	 */
	uint16_t mid;
	assert(mosq);
#ifdef WITH_THREADING
	pthread_mutex_lock(&mosq->mid_mutex);
#endif	
	mosq->last_mid++;
	if(mosq->last_mid == 0) mosq->last_mid++;
	mid = mosq->last_mid;
#ifdef WITH_THREADING
	pthread_mutex_unlock(&mosq->mid_mutex);
#endif

	return mid;
}


#ifdef WITH_TLS
int mosquitto__hex2bin_sha1(const char *hex, unsigned char **bin)
{
	unsigned char *sha, tmp[SHA_DIGEST_LENGTH];

	if(mosquitto__hex2bin(hex, tmp, SHA_DIGEST_LENGTH) != SHA_DIGEST_LENGTH){
		return MOSQ_ERR_INVAL;
	}

	sha = mosquitto__malloc(SHA_DIGEST_LENGTH);
	if(!sha){
		return MOSQ_ERR_NOMEM;
	}
	memcpy(sha, tmp, SHA_DIGEST_LENGTH);
	*bin = sha;
	return MOSQ_ERR_SUCCESS;
}

int mosquitto__hex2bin(const char *hex, unsigned char *bin, int bin_max_len)
{
	BIGNUM *bn = NULL;
	int len;
	int leading_zero = 0;
	int start = 0;
	size_t i = 0;

	/* Count the number of leading zero */
	for(i=0; i<strlen(hex); i=i+2) {
		if(strncmp(hex + i, "00", 2) == 0) {
			leading_zero++;
			/* output leading zero to bin */
			bin[start++] = 0;
		}else{
			break;
		}
	}

	if(BN_hex2bn(&bn, hex) == 0){
		if(bn) BN_free(bn);
		return 0;
	}
	if(BN_num_bytes(bn) + leading_zero > bin_max_len){
		BN_free(bn);
		return 0;
	}

	len = BN_bn2bin(bn, bin + leading_zero);
	BN_free(bn);
	return len + leading_zero;
}
#endif

void util__increment_receive_quota(struct mosquitto *mosq)
{
	if(mosq->msgs_in.inflight_quota < mosq->msgs_in.inflight_maximum){
		mosq->msgs_in.inflight_quota++;
	}
}

void util__increment_send_quota(struct mosquitto *mosq)
{
	if(mosq->msgs_out.inflight_quota < mosq->msgs_out.inflight_maximum){
		mosq->msgs_out.inflight_quota++;
	}
}


void util__decrement_receive_quota(struct mosquitto *mosq)
{
	if(mosq->msgs_in.inflight_quota > 0){
		mosq->msgs_in.inflight_quota--;
	}
}

void util__decrement_send_quota(struct mosquitto *mosq)
{
	if(mosq->msgs_out.inflight_quota > 0){
		mosq->msgs_out.inflight_quota--;
	}
}


int util__random_bytes(void *bytes, int count)
{
	int rc = MOSQ_ERR_UNKNOWN;

#ifdef WITH_TLS
	if(RAND_bytes(bytes, count) == 1){
		rc = MOSQ_ERR_SUCCESS;
	}
#elif defined(HAVE_GETRANDOM)
	if(getrandom(bytes, (size_t)count, 0) == count){
		rc = MOSQ_ERR_SUCCESS;
	}
#elif defined(WIN32)
	HCRYPTPROV provider;

	if(!CryptAcquireContext(&provider, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)){
		return MOSQ_ERR_UNKNOWN;
	}

	if(CryptGenRandom(provider, count, bytes)){
		rc = MOSQ_ERR_SUCCESS;
	}

	CryptReleaseContext(provider, 0);
#else
	int i;

	for(i=0; i<count; i++){
		((uint8_t *)bytes)[i] = (uint8_t )(random()&0xFF);
	}
	rc = MOSQ_ERR_SUCCESS;
#endif
	return rc;
}


int mosquitto__set_state(struct mosquitto *mosq, enum mosquitto_client_state state)
{
#ifdef WITH_THREADING
	pthread_mutex_lock(&mosq->state_mutex);
#endif
#ifdef WITH_BROKER
	if(mosq->state != mosq_cs_disused)
#endif
	{
		mosq->state = state;
	}
#ifdef WITH_THREADING
	pthread_mutex_unlock(&mosq->state_mutex);
#endif

	return MOSQ_ERR_SUCCESS;
}

enum mosquitto_client_state mosquitto__get_state(struct mosquitto *mosq)
{
	enum mosquitto_client_state state;
#ifdef WITH_THREADING
	pthread_mutex_lock(&mosq->state_mutex);
#endif
	state = mosq->state;
#ifdef WITH_THREADING
	pthread_mutex_unlock(&mosq->state_mutex);
#endif

	return state;
}

#ifndef WITH_BROKER
void mosquitto__set_request_disconnect(struct mosquitto *mosq, bool request_disconnect)
{
#ifdef WITH_THREADING
	pthread_mutex_lock(&mosq->state_mutex);	
#endif
	mosq->request_disconnect = request_disconnect;
#ifdef WITH_THREADING
	pthread_mutex_unlock(&mosq->state_mutex);
#endif	
}

bool mosquitto__get_request_disconnect(struct mosquitto *mosq)
{
	bool request_disconnect;
#ifdef WITH_THREADING
	pthread_mutex_lock(&mosq->state_mutex);
#endif
	request_disconnect = mosq->request_disconnect;
#ifdef WITH_THREADING
	pthread_mutex_unlock(&mosq->state_mutex);
#endif

	return request_disconnect;
}
#endif
