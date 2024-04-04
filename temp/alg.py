from math import gcd

# Define a function to calculate LCM
def lcm(x, y):
    return x * y // gcd(x, y)

# List of numbers
numbers = [10, 28, 35, 40, 45, 70]

# Initialize lcm as the first number in the list
lcm_result = numbers[0]

# Calculate LCM iteratively for each number in the list
for num in numbers[1:]:
    lcm_result = lcm(lcm_result, num)

print("Least Common Multiple:", lcm_result)
