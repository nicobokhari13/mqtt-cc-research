#!/bin/bash
python3 subscriber.py sub000 topic/1%latency%25,topic/3%latency%23,topic/5%latency%41 &
python3 subscriber.py sub001 topic/0%latency%33,topic/1%latency%18,topic/2%latency%34,topic/4%latency%12,topic/5%latency%49 &
