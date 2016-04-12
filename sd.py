# find SD
import math

ary = [21, 24, 24, 27, 29]

def find_sd(lst):
    """ return the standard deviation of a list"""
    count = len(lst)
    u = sum(lst) / count
    y = 0
    for x in lst:
        y += (x - u) ** 2.0
    return math.sqrt(y/count)

if __name__ == '__main__': 
    print find_sd(ary)