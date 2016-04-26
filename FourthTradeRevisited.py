import gamemaster
import time

sf = gamemaster.StockFighter("dueling_bulldozers")
# sf = gamemaster.StockFighter("sell_side")
stock = sf.tickers
start = time.time()
end = time.time()
prevQuote = None
bid_stream = []
ask_stream = []

def find_median(lst):
    if len(lst) % 2 == 1:
        median = lst[((len(lst) + 1) / 2) - 1]        
    else:
        median = float(sum(lst[(len(lst) / 2) - 1:(len(lst) / 2) + 1])) / 2.0
    return median

def find_iqr(lst):
    lst.sort()
    q1 = find_median(lst[:len(lst) // 2])
    q3 = find_median(lst[len(lst) // 2:])
    iqr = q3 - q1
    return lst[0], lst[-1], iqr

def is_outlier(lst, number):
    i_min, i_max, i_iqr = find_iqr(lst)
    low_outlier = i_min - 1.5 * i_iqr
    high_outlier = i_max + 1.5 * i_iqr
    if number > high_outlier or number < low_outlier:
        # print "\tOUTLIER %d is outlier min %d, max %d, iqr %d" % (number, i_min, i_max, i_iqr),  
        return True
    else:
        # print "number %d is within min %d, max %d, iqr %d" % (number, i_min, i_max, i_iqr),
        return False


while end - start < 50:                
    try:
        quote = sf.quotes[-1]
 
        if not quote == prevQuote:
            # print "bid Depth %r, ask Depth %r ts %r" % (quote['bidDepth'], quote['askDepth'], quote['quoteTime'])
            ask_outlier = False
            bid_outlier = False

            if len(bid_stream) > 20:
                if is_outlier(bid_stream, quote['bidDepth']):
                    print "%r is an outlier for bid" %(quote['bidDepth'])
            if quote['bidDepth'] > 0 and bid_outlier is False:
                bid_stream.append(quote["bidDepth"])
            
            if len(ask_stream) > 20:
                if is_outlier(ask_stream, quote['askDepth']):
                    print "%r is an outlier for ask" %(quote['askDepth'])
            if quote['askDepth'] > 0 and ask_outlier is False:
                ask_stream.append(quote["askDepth"])
            prevQuote = quote
    except:
        quote = None
    

    # oBook = sf.get_order_book(stock)
    # print "printing\n %r \n and \n %r\n" % (oBook.json(), quote)
    # print "*****\nOrderBook Bid , quotes BestBid\n" % (s_BestBid, q_BestBid)
    # print "*****\nOrderBook Ask , quotes BestAsk\n" % (s_BestAsk, q_BestAsk)
    end = time.time()
sf.make_graphs()
    