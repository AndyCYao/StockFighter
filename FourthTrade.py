import gamemaster
import time
import json
"""
Feb 28th 2016 - Fourth Trade - Dueling Bull Dozers.

Make $10,000 in profit while minimizing your exposure

"""


start = time.time()
end = time.time()

sf = gamemaster.StockFighter("dueling_bulldozers")
stock = sf.tickers

positionSoFar = 0       # if negative means short if positive long total filled
expectedPosition = 0    # this is if both filled and to be filled are accounted for (cant be over +/-1500)
premium = 1.025
ma_20_list = []    # moving average 20 lets the script know current trend.
ma_20 = 0
nav = 0
orderIDList = 0


def warning_big_order(orderbook):
    """affect the buy / sell conditions.
    checks the relative proportion of depth on bothsides.
    if bid depth is much bigger than ask, then stop all buy
    if bid depth is much smaller, do vice versa.
    """
    pass


def buy_condition(tSpread, tExpectedPosition):
    """to be tailored for each level."""
    if tSpread > 0.005 and tExpectedPosition <= 0:
        return True
    return False


def sell_condition(tSpread, tExpectedPosition):
    """to be tailored for each level."""
    if tSpread > 0.005 and tExpectedPosition >= 0:
        return True
    return False

try:
    while nav < 250000:
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
                Spread = "{0:%}".format(Difference / (BestAsk + 0.0))
            else:
                Spread = 0
        except ZeroDivisionError:
            Spread = 0

        end = time.time()
     
        if len(ma_20_list) > 20:  # if theres stuff in ma_20_list
            ma_20_list.pop(0)
        ma_20_list.append(sf.get_quote(stock).get("last"))
        curr_count = len(ma_20_list)
        for x in ma_20_list:
            # print x,
            ma_20 += x + 0.0
        ma_20 = int(ma_20 / curr_count)
     
        nav = cash + positionSoFar * sf.get_quote(stock).get("last") * (.01)
        nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below
        
        print "T%d Pos. %d, Expected Pos. %d Best Ask %r , Best Bid %r, Spread %r, average %r, NAV %s" % \
            ((end - start), positionSoFar, expectedPosition, BestAsk, BestBid, Spread, ma_20, nav_currency)

        time.sleep(2)  # slow things down a bit, because we are querying the same information.

        if buy_condition(Spread, expectedPosition):
            buyOrder = sf.make_order(BestBid, q_bid, stock, "buy", "limit")
            buyPrice = buyOrder.get('price')
            buyID = buyOrder.get('id')
            print "BBBBB placed buy ord. - %d units at %d ID %d" % (q_bid, buyPrice, buyID)
        
        if sell_condition(Spread, expectedPosition):
            sellOrder = sf.make_order(int(BestAsk * premium), q_ask, stock, "sell", "limit")
            sellPrice = sellOrder.get('price')
            sellID = sellOrder.get('id')
        
            print "SSSSS placed sold ord. - %d units at %d ID %d" % (q_ask, sellPrice, sellID)

        end = time.time()

except KeyboardInterrupt:
    print "ctrl+c pressed!"
    EndLog = open("results.txt", "w")
    json.dump(orderIDList, EndLog)
    EndLog.close()
