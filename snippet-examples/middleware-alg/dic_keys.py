assignments = {"topic":43, "another/topic":34}
print(type(assignments))
print(assignments)
keys = list(assignments.keys())
for i in range(len(keys)):
    print(i)
    print(keys[i])
anotherVar = list(assignments.keys())
print(anotherVar)