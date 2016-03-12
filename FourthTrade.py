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


def large_depth():
    """affect the buy / sell conditions.
    checks the relative proportion of depth on bothsides.
    if bid depth is much bigger than ask, then stop all buy, and sell
    if bid depth is much smaller, do vice versa.
    """
    try:
        depth_ratio = sf.get_quote(stock).get("bidDepth") / sf.get_quote(stock).get("askDepth")
        if depth_ratio >= 1.5:
            return "large_bids_depth"
        elif depth_ratio <= 1.5:
            return "large_asks_depth"
        else:
            return "regular"
    except ValueError as e:
        print e
    except ZeroDivisionError:
        print "zero divided"
        return "regular"


def buy_condition(tSpread, tExpectedPosition, positionSoFar, tBestBid, tMA):
    """to be tailored for each level.
        will buy if the price is not above MA20 price.
    """
    # if large_depth() == "large_bids_depth":
    if tSpread > 0.005 and tExpectedPosition <= 0 and positionSoFar < 500 and tBestBid < tMA:
        return True
    # return False


def sell_condition(tSpread, tExpectedPosition, positionSoFar, tBestAsk, tMA):
    """to be tailored for each level.
        will sell if the price is not below MA20 price.
    """
    #if large_depth() == "large_asks_depth":
    if tSpread > 0.005 and tExpectedPosition >= 0 and positionSoFar > -500 and tBestAsk > tMA:
        return True
    # return False


def identify_unfilled_orders(orderList, callback):
    """check through orderIDlist, and return a list of
    orders that is not gonna be filled at the moment because
    the price is out the money.
    """
    for x in orderList["orders"]:
        if x["open"]:
            if callback(x):
                print "\n\tCancelling units %s - id %s at %s \n" % (x["qty"], x["id"], x["price"]),
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
    
    if timeDiff < datetime.timedelta(seconds=15):  # if longer than 30 sec. then cancel it. since the order is clearly overtaken by other
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
        print("Should Cancel ID%s its been %s since ordered") % (order["id"], timeDiff)
        return True
    return False

try:
    while nav < 250000:
        time.sleep(1)    # slow things down a bit, because we are querying the same information.
        orderIDList = sf.status_for_all_orders_in_stock(stock)
        positionSoFar, cash, expectedPosition = sf.update_open_orders(orderIDList.json())
        oBook = sf.get_order_book(stock)

        BestAsk = sf.read_orderbook(oBook, "asks", "price")
        BestBid = sf.read_orderbook(oBook, "bids", "price")
        q_bid = min(sf.read_orderbook(oBook, "bids", "qty"), 250)  # min of 250 because we only have 1000 on either side of pos to work with.
        q_ask = min(sf.read_orderbook(oBook, "asks", "qty"), 250)

        Difference = BestAsk - BestBid

        try:
            if BestBid > 0:
                Spread = Difference / (BestAsk + 0.0)
                sell_discount = 1 - (Spread * .2)
                buy_premium = 1 + (Spread * .15)
                Spread = "{0:.0%}".format(Spread)
            else:
                Spread = 0
        except ZeroDivisionError:
            Spread = 0

        end = time.time()
     
        if len(ma_20_list) > 20:  # Moving average 20 ticks
            ma_20_list.pop(0)
        ma_20_list.append(sf.get_quote(stock).get("last"))
        # print(ma_20_list)
        ma_20 = sum(ma_20_list) / len(ma_20_list)
     
        nav = cash + positionSoFar * sf.get_quote(stock).get("last") * (.01)

        nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below
        print "T%d Pos. %d, Expected Pos. %d, B_Bid, %r B_Ask %r , Last %r, Spread %r, average %r, NAV %s" % \
            ((end - start), positionSoFar, expectedPosition, BestBid, BestAsk, ma_20_list[-1], Spread, ma_20, nav_currency)
                
        if buy_condition(Spread, expectedPosition, positionSoFar, BestBid, ma_20):
            buyOrder = sf.make_order(int(BestBid * buy_premium), q_bid, stock, "buy", "limit")
            buyPrice = buyOrder.get('price')
            buyID = buyOrder.get('id')
            print "\n\tBBBBB placed buy ord. +%d units at %d ID %d \n" % (q_bid, buyPrice, buyID)
        
        if sell_condition(Spread, expectedPosition, positionSoFar, BestAsk, ma_20):
            sellOrder = sf.make_order(int(BestAsk * sell_discount), q_ask, stock, "sell", "limit")
            sellPrice = sellOrder.get('price')
            sellID = sellOrder.get('id')
        
            print "\n\tSSSSS placed sold ord. -%d units at %d ID %d \n" % (q_ask, sellPrice, sellID)

        # check if some orders need to be cancelled ###
        # start with sell orders.
    
        identify_unfilled_orders(orderIDList.json(), should_cancel_unfilled)
   
except KeyboardInterrupt:
    print "ctrl+c pressed!"
