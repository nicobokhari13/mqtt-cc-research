# Frequently Ran Commands
- To delete all *.o files
  - `find . -type f -name '*.o' -delete`
- Find mosquitto pid and kill process
  - `ps aux | grep mosquitto`
- Simulated Publishers
  - `python3 sensor.py sim 100 d8:3a:dd:90:ee:62 0.1`
  - `python3 sensor.py sim 100 d8:3a:dd:90:ee:38 0.1`
- Simulated Subscribers
  - `python3 subscriber.py sensor/temperature%latency%10,sensor/humidity%latency%30,sensor/airquality%latency%50`
  - `python3 subscriber.py sensor/temperature%latency%28,sensor/humidity%latency%45`
  - `python3 subscriber.py sensor/humidity%latency%12,sensor/airquality%latency%20`
- Raspberry Pi
  ```bash
  cd repos/research/mqtt_cc_research
  source prototype/dev/bin/activate
  cd testbed/devs
  ```
- TCP Dump
  - `sudo tcpdump -i wlp0s20f3 port 1883 -w filname.pcap`
  - `sudo tcpdump -i lo port 1883 -w filname.pcap`
  - `tshark -r input.pcap -w output.pcap "tcp.len > 32000"`
- To run subscribers on windows, use `python` not `python3`


New Algorithm with Sensing + Communication Energies
```bash
python3 proto_client.py /home/devnico/repos/research/mqtt_cc_research/prototype/src/devs/devices.csv sim 900 0.05 0.01 2 

python3 subscriber.py sub000 topic/0%latency%5

python3 subscriber.py sub001 topic/1%latency%6

python3 subscriber.py sub002 topic/2%latency%10

python3 subscriber.py sub003 topic/3%latency%12

python3 sensor.py sim dev000 100 0.05 0.01

python3 sensor.py sim dev001 100 0.05 0.01

```