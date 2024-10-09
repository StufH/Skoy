import sys
sys.set_int_max_str_digits(0)
count = 0

test = ((2**82589933)-1)
print(test)
print("")
from time import sleep
from tqdm import tqdm
'''
while test != 0:
    test //= 10
    count += 1

print("Number of digits: " + str(count))


if test > 1:

    for i in range(2, (test // 2) + 1):
        for y in tqdm(range(1)):

        # If num is divisible by any number between
        # 2 and n / 2, it is not prime

            if (test % i) == 0:
                print("is not a prime number")
                break
    else:
        print("is a prime number")
else:
    print("is not a prime number")
'''
