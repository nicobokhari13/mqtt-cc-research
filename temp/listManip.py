import math
import time
import random
nums = [random.randint(1, 100) for i in range(10)]
nums_min = min(nums)
threshold = math.ceil(nums_min / 2) - 1
print(f"threshold = {threshold}")
start = time.time()
# Create a list of numbers to remove
removes = [num for num in nums if (num % nums_min < threshold) or ((nums_min - num % nums_min) < threshold)]
# Remove the numbers from the original list
nums = [num for num in nums if num not in removes]
stop = time.time()
print(f"duration: {stop - start}")
# Append the minimum number to the list
nums.append(nums_min)
print(nums_min)
print(nums)
