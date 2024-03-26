import math
# nums = [random.randint(1, 100) for i in range(10)]
nums = [10, 12, 20, 37, 35, 45]
print(nums)
nums_min = min(nums)
threshold = math.ceil(nums_min / 2) - 1
print(f"threshold = {threshold}")
# Create a list of numbers to remove
removes = [num for num in nums if (num % nums_min < threshold) or ((nums_min - num % nums_min) < threshold)]
# Remove the numbers from the original list
nums = [num for num in nums if num not in removes]
nums.append(nums_min)
numExecutions = 0
for i in range(len(nums)):
    numExecutions += math.floor(60 / nums[i])
    print(f"executions now at: {numExecutions}")
print(nums_min)
print(nums)
print(numExecutions)
