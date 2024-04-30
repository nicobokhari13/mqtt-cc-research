freqCopy = [5,6,10, 12]

threshold = 3
# if freqCopy has any items other than the minimum just removed,
frequency_multiples = ()
same_execution_group = []
group_min = None
num_executions = 0 
multiplier = 2

if freqCopy:
    frequency_multiples = set(freqCopy)
    # check if there exists a number in the set of frequency_multiples where |multiplreOfFreq - freq| < threshold
    for freq in freqCopy: 
        multipleOfFreq = freq * multiplier
        while multipleOfFreq < 60:
            frequency_multiples.add(multipleOfFreq)
            multiplier+=1
            multipleOfFreq = freq * multiplier
        multiplier = 1
    # convert the multiples back into a list for sorting in order
    print(frequency_multiples, type(frequency_multiples))
    frequency_multiples = list(frequency_multiples)
    frequency_multiples.sort()
    print(frequency_multiples, type(frequency_multiples))
    
    # after inserting all all multiples, loop through again, find a group of elements that are within threshold
    for i in range(len(frequency_multiples)):
        if i == 0: # if this is the first element
            # then add it to the execution group 
            same_execution_group.append(frequency_multiples[i])
            group_min = frequency_multiples[i]
            print("added the first element")
        else:
            if abs(frequency_multiples[i] - group_min) < threshold:
                # if the absolute value between the frequency multiple and group min is less than threshold
                # then add it to the same execution group
                same_execution_group.append(frequency_multiples[i])
                # the group_min shouldn't change 
                print("element in the same execution")
            else:
                # if this element is not within the group_min's threshold, then increase the number of executions, 
                num_executions+=1
                same_execution_group.clear()
                same_execution_group.append(frequency_multiples[i])
                group_min = frequency_multiples[i]
                print("element not in the same execution, resetting group")
                # reset the same_execution_group, and add the current element
                # increment the number of executions
                # reset group min
        print("num execution = ", num_executions)
        print('====')
        print("index = ", i)
        print("group = ", same_execution_group)

    print()
    if len(same_execution_group):
        num_executions+=1

print("for freqs ", freqCopy)
print("number of executions = ", num_executions)



