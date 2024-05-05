#!/bin/bash
python3 subscriber.py sub000 topic/0%latency%33,topic/1%latency%37,topic/2%latency%14,topic/3%latency%7,topic/4%latency%16,topic/5%latency%22 &
python3 subscriber.py sub001 topic/0%latency%51,topic/1%latency%36,topic/2%latency%12,topic/3%latency%53,topic/5%latency%34 &
