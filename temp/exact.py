freq = [5,11,17]
observation = 60
times = []
execution_times = []
threshold = 5
for frequency in freq:
    times = list(range(0,observation + 1, frequency))
    execution_times.extend(times)
execution_times.sort()
print(execution_times)
effective_executions = 0
last_execution_end = -threshold

for time in execution_times:
    if time >= last_execution_end + threshold:
        effective_executions+=1
        last_execution_end = time
    
print(effective_executions)
