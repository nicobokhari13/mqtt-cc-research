#!/bin/bash
python3 subscriber.py sub000 topic/0%latency%37,topic/1%latency%13,topic/2%latency%18,topic/3%latency%45,topic/4%latency%47,topic/5%latency%33 &
python3 subscriber.py sub001 topic/0%latency%24,topic/3%latency%9 &
