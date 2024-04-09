# To Do
- read dump files
- resolve broker wait time
- debug metrics on publishers
- run simulation
- consider script to randomize latencies of subscribers

- Approaches (Vary # topics, Vary # publishers, Vary randomness of subscriber latencies)
  - No algorithm (no lat Qos and no selection, all publishers publish where they are capable)
  - RR (yes lat Qos selection = ordered)
  - Random (yes lat Qos, selection not ordered)
  - Algorithm (same energy_executions + algorithm rerun)
- Contribution
  - Test Bed
  - Varying the conccurrent_execution_thresholds