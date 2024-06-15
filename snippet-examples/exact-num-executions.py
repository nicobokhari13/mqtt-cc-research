# TODO: Acquire the exact number of effective executions the set of frequencies performs within the observation period
    # analyze time complexity? 
# for example, at time stamp 10, frequences [5,11] both can be batched as 10 = 5 * 2 and freq 11 is within a 5 unit threshold of 10
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
