# To Do

## 5-6-24 Monday Planning
- Finished acquiring data
- Perform analysis
- Start writing paper with % of average battery consumption reduction for the system or device

## 5-4-24 Saturday Planning
- Outline areas of codebase for the following features
  - save results for a single round in the same file
  - random task allocation algorithm
- Determine number of rounds for each algorithm
- Remove all metrics csv

## Planning 
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

