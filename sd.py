# find SD
import json
# import datetime
from dateutil import tz, parser

def find_median(lst):
    if len(lst) % 2 == 1:
        median = lst[((len(lst) + 1) / 2) - 1]        
    else:
        median = float(sum(lst[(len(lst) / 2) - 1:(len(lst) / 2) + 1])) / 2.0
    return median

def find_iqr(lst):
    lst.sort()
    # print "min is %d" % (lst[0])
    # print "max is %d" % (lst[-1])
    # print "median is %d" % (find_median(lst))
    q1 = find_median(lst[:len(lst) // 2])
    q3 = find_median(lst[len(lst) // 2:])
    iqr = q3 - q1
    return lst[0], lst[-1], iqr

def is_outlier(lst, number):
    i_min, i_max, i_iqr = find_iqr(lst)
    low_outlier = i_min - 3 * i_iqr
    high_outlier = i_max + 3 * i_iqr
    if number > high_outlier or number < low_outlier:
        # print "number %d is outlier min %d, max %d, iqr %d" % (number, i_min, i_max, i_iqr),  
        return True
    else:
        # print "number %d is within min %d, max %d, iqr %d" % (number, i_min, i_max, i_iqr),
        return False

if __name__ == '__main__':
    """Checking if the quote stream can detect outliers"""
    file = json.loads(open("currentInfo.json").read())
    bid_stream = []
    ask_stream = []
    for x in file:        
        outlier = False        
        if len(bid_stream) > 20:
            print(is_outlier(bid_stream, x['bidDepth']))
        if not x['bidDepth'] == 0:
            bid_stream.append(x["bidDepth"])
        
        if len(ask_stream) > 20:
            outlier = is_outlier(ask_stream, x['askDepth'])
            # print("time %r" % (x['quoteTime']))

        if x['askDepth'] > 0 and outlier is False:
            ask_stream.append(x["askDepth"])
