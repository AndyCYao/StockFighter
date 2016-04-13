# find SD
import math

ary = [29, 24, 24, 27, 21]


def find_sd(lst):
    """return the standard deviation of a list."""
    if len(lst) < 1:
        raise ValueError('mean requires at least one data point')
    count = len(lst)
    u = sum(lst) / count
    y = 0
    for x in lst:
        y += (x - u) ** 2.0
    return math.sqrt(y / (count - 1))

def find_median(lst):
    if len(lst) % 2 == 1:
        median = lst[((len(lst) + 1) / 2) - 1]        
    else:
        median = float(sum(lst[(len(lst) / 2) - 1:(len(lst) / 2) + 1])) / 2.0
    return median

def find_iqr(lst):
    lst.sort()
    print "min is %d" % (lst[0])
    print "max is %d" % (lst[-1])
    print "median is %d" % (find_median(lst))
    q1 = find_median(lst[:len(lst) // 2])
    q3 = find_median(lst[len(lst) // 2:])
    iqr = q3 - q1
    print iqr
    return lst

if __name__ == '__main__': 
    # print find_sd(ary)
    print(find_iqr(ary))