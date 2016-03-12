import gamemaster
import time
import json
import datetime  # StockFighter uses ISO format so need this to convert our time
"""
Feb 28th 2016 - Fourth Trade - Dueling Bull Dozers.

Make $250000 in profit while minimizing your exposure

note: if an order is not being filled , the price has most likely gone out of 
trading range. should cancel and rebid. 
"""


start = time.time()
end = time.time()

sf = gamemaster.StockFighter("dueling_bulldozers")
stock = sf.tickers

positionSoFar = 0       # if negative means short if positive long total filled
expectedPosition = 0    # this is if both filled and to be filled are accounted for (cant be over +/-1500)
ma_20_list = []    # moving average 20 lets the script know current trend.
ma_20 = 0
nav = 0
orderIDList = 0

"""
Parameters for execution and order cancels
"""
timeToWait = 5
gapPercent = .01 # how much different in % each order will be
worstCase = .05  # how much different the best offer and worst offer will be
""""""

def buy_condition(tExpectedPosition, positionSoFar, tBestBid, tMA):
    """to be tailored for each level.
        will buy if the price is not above MA20 price.
    """
    if tBestBid != 0:
        if tExpectedPosition <= 0 and positionSoFar < 500 and tBestBid < tMA:
            return True
    return False

def sell_condition(tExpectedPosition, positionSoFar, tBestAsk, tMA):
    """to be tailored for each level.
        will sell if the price is not below MA20 price.
    """
    if tBestAsk != None or tBestAsk != 0:
        if tExpectedPosition >= 0 and positionSoFar > -500 and tBestAsk > tMA:
            return True
    

def identify_unfilled_orders(orderList, callback):
    """check through orderIDlist, and return a list of
    orders that is not gonna be filled at the moment because
    the price is out the money.
    """
    for x in orderList["orders"]:
        if x["open"]:
            if callback(x):
                print "\n\tCancelling %s units %s - id %s at %s \n" % (x["direction"], x["qty"], x["id"], x["price"]),
                sf.delete_order(stock, x["id"])


def should_cancel_unfilled(order):
    """if this order is out of money, then cancel it"""
    s_BestAsk = sf.read_orderbook(oBook, "asks", "price")
    s_BestBid = sf.read_orderbook(oBook, "bids", "price")
    price = order["price"]

    # this is in ISO 8601 time. stripping the microseconds we are not that concern
    ts = order["ts"].split(".")[0]
    o_time = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
    
    timeDiff = datetime.datetime.utcnow() - o_time
    
    if timeDiff < datetime.timedelta(seconds= timeToWait):
        if order["direction"] == "buy":
            diff = (s_BestBid - price) / price
            if diff < -.1:
                print "\tShould cancel ID%s %s %s because its price is %s and Best Bid is %s" % (order["id"], order["direction"], order["qty"],
                    order["price"], s_BestBid)
                return True
        else:
            diff = (s_BestAsk - price) / price
            if diff > .1:
                print "\tShould cancel ID%s %s %s because its price is %s and Best Ask is %s" % (order["id"], order["direction"], order["qty"],
                    order["price"], s_BestAsk)
                return True
    else:
        print("Should cancel ID%s its been %s since ordered") % (order["id"], timeDiff)
        return True
    return False

try:
    while nav < 250000:
        time.sleep(1)    # slow things down a bit, because we are querying the same information.
        orderIDList = sf.status_for_all_orders_in_stock(stock)
        positionSoFar, cash, expectedPosition = sf.update_open_orders(orderIDList.json())
        oBook = sf.get_order_book(stock)

        # will multiply base on the below info with gapPercent
        bestAsk = sf.read_orderbook(oBook, "asks", "price")
        bestBid = sf.read_orderbook(oBook, "bids", "price")
        q_bid = min(sf.read_orderbook(oBook, "bids", "qty"), 30)
        q_ask = min(sf.read_orderbook(oBook, "asks", "qty"), 30)

        end = time.time()
     
        if len(ma_20_list) > 20:  # Moving average 20 ticks
            ma_20_list.pop(0)
        ma_20_list.append(sf.get_quote(stock).get("last"))
        # print(ma_20_list)
        ma_20 = sum(ma_20_list) / len(ma_20_list)
     
        nav = cash + positionSoFar * sf.get_quote(stock).get("last") * (.01)
        nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below
        print "T%d Pos. %d, Expected Pos. %d, B_Bid, %r B_Ask %r , Last %r, average %r, NAV %s" % \
            ((end - start), positionSoFar, expectedPosition, bestBid, bestAsk, ma_20_list[-1], ma_20, nav_currency)
        
   
        if buy_condition(expectedPosition, positionSoFar, bestBid, ma_20):
            # loop through the gapPercent and make multiple bids.
            increment = int(bestBid * gapPercent * -1)
            worstBid = int(bestBid * (1 - worstCase))
            q_increment = int(q_bid * gapPercent)
            q_actual = q_bid
            print "initial %s %s" % (q_actual, q_increment)
            for actualBid in range(bestBid, worstBid , increment):
                # print actualBid, q_actual
                buyOrder = sf.make_order(actualBid, q_actual, stock, "buy", "limit")
                buyPrice = buyOrder.get('price')
                buyID = buyOrder.get('id')
                print "\n\tBBBBB placed buy ord. +%d units at %d ID %d" % (q_bid, buyPrice, buyID)
                q_actual -= q_increment

        if sell_condition(expectedPosition, positionSoFar, bestAsk, ma_20):
            # loop through the gapPercent and make multiple bids.
            increment = int(bestAsk * gapPercent)
            worstAsk = int(bestAsk * (1 + worstCase))
            q_increment = int(q_ask * gapPercent)
            q_actual = q_ask
            # print "initial %s %s %s" % (q_actual, q_increment, worstAsk)
            for actualAsk in range(bestAsk, worstAsk , increment):
                sellOrder = sf.make_order(actualAsk, q_actual, stock, "sell", "limit")
                sellPrice = sellOrder.get('price')
                id = sellOrder.get('id')
                print "\n\tSSSSS placed sell ord. -%d units at %d ID %d" % (q_ask, sellPrice, id)
                q_actual -= q_increment


        # check if some orders need to be cancelled ###
        # start with sell orders.
        identify_unfilled_orders(orderIDList.json(), should_cancel_unfilled)
   
except KeyboardInterrupt:
    print "ctrl+c pressed!"
