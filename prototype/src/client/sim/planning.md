# Planning 

- Consider energy consumption helper to acquire the timeline of frequnecies over period T
- Publishing units should keep a frequency timeline with all frequency "timestamps" during the observation period
- Topic Container should already create a timeline from 0 - T observation period with each mulitple of frequencies in the dictionary 
- Since T = 1 hour (3,600,000 milliseconds)
  - number of sensing tasks = # frequencies
  - number of communication tasks = # effective executions = calculateExecutions()
    - consider the simple function in exact.py
- round robin tracks the order of devices for each topic, as in rotate topics in order of devices (alphabetically)
- Configurables:
  - threshold
  - smallest latency - maximum latency in milliseconds