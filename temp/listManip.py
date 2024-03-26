import math

nums = [10, 12, 20, 37, 45]
goods = []
nums_min = min(nums)
nums.remove(nums_min)
threshold = math.ceil(nums_min / 2) - 1
print(f"threshold = {threshold}")
for i in range(len(nums)):
    if i > len(nums):
        print(f"at index {i}, breaking now")
        break
    print(f"index {i} value {nums[i]}")
    # if the number is within the threshold 
    # 12 % 10 = 2 < 4, removed 2 = -8 mod 10
    # 20 % 10 = 0 < 4, removed 0 = -10 mod 10
    # 37 % 10 = 7 > 4, 7 = -3 mod 10, 10 - 7 = 3
    # 45 % 10 = 5 > 4 OR 5 = -5 mod 10
    print(f"difference: {nums[i] % nums_min}, mod equiv {nums_min - nums[i] % nums_min}")
    print(f"    {nums[i] % nums_min < threshold}")
    print(f"    {(nums_min - nums[i] % nums_min) < threshold}")
    if (nums[i] % nums_min < threshold) or ((nums_min - nums[i] % nums_min) < threshold):
        # remove it from the list
        goods.append(nums[i])
    print(f"    goods: {goods}")
    print(f"    nums: {nums}")
diff = set(nums) - set(goods)
diff = list(diff)
print(f"diff = {diff}")


    
