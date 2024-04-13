#!/bin/bash
python3 subscriber.py sub000 topic/0%latency%45,topic/1%latency%28,topic/2%latency%11,topic/3%latency%44,topic/5%latency%38 &
python3 subscriber.py sub001 topic/0%latency%20,topic/1%latency%25,topic/2%latency%14,topic/4%latency%21,topic/5%latency%19 &
