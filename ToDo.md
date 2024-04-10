# To Do
- remove password need
- use username as a means to debug and identify subscribers + publishers
- copy over scripts for prototype
- script to generate publishers, subscribers, and topics lists files from input #s
- script reads files, puts data into lists, randomly pairs publishers/subs with topics
- based on type of simulation, perform different database actions

- Approaches (Vary # topics, Vary # publishers, Vary randomness of subscriber latencies)
  - No algorithm (no lat Qos and no selection, all publishers publish where they are capable)
  - RR (yes lat Qos selection = ordered)
  - Random (yes lat Qos, selection not ordered)
  - Algorithm (same energy_executions + algorithm rerun)
- Contribution
  - Test Bed
  - Varying the conccurrent_execution_thresholds