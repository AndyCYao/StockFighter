import gamemaster
import time
import datetime
import json
"""
Feb 25th 2016 Third Trade sell_side. Here is the approach currently.
1.) script reads the most favorable quotes in the read_orderbook retrieve
    their bid / ask / qty.
2.) since the max long / short position is 1000, i cant make too risky trades.
    so if the qty is > 100
    i should just cap it at 100
3.) Apply a mark up on the sell side to capture the premium
4.) reguarly check the position using update_open_orders
5.) Net Asset Value is the unrealized gain or loss of asset in hand
    based on the diff. of current quote - purchased price
Feb 29th 2016 -
1.) add a way to check how many position pending ontop of the total filled.
"""


start = time.time()
end = time.time()

sf = gamemaster.StockFighter("sell_side")
stock = sf.tickers

premium = 1.025
ma_20_list = []    # moving average 20 lets the script know current trend.
ma_20 = 0
nav = 0


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

def identify_unfilled_orders(orderList, callback):
        """check through orderIDlist, and return a list of
        orders that is not gonna be filled at the moment because
        the price is out the money.
        """
        for x in orderList["orders"]:
            if x["open"]:
                if callback(x):
                    print "\n\tCancelling %s %s units at %s ID %s \n" % (x["direction"], x["qty"], x["price"], x["id"])
                    sf.delete_order(stock, x["id"])

def should_cancel_unfilled(order):
    """if this order is out of money, then cancel it"""
    oBook = sf.get_order_book(stock)
    s_BestAsk = sf.read_orderbook(oBook, "asks", "price", 1)
    s_BestBid = sf.read_orderbook(oBook, "bids", "price", 1)
    price = order["price"]

    # this is in ISO 8601 time. stripping the microseconds we are not that concern
    ts = order["ts"].split(".")[0]
    o_time = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
    
    timeDiff = datetime.datetime.utcnow() - o_time
    
    if timeDiff < datetime.timedelta(seconds=5):
        if order["direction"] == "buy":
            diff = (s_BestBid - price) / price
            if diff < -.1:
                return True
        else:
            diff = (s_BestAsk - price) / price
            if diff > .1:
                return True
    else:
        return True
    return False


try:
    sf.execution_venue_ticker(sf.execution_socket)  # start the thread for update the status.
    while nav < 12000:
        if abs(sf.positionSoFar) > 1000:
            break

        orderIDList = sf.status_for_all_orders_in_stock(stock)
        # sf.positionSoFar, sf.cash, sf.expectedPosition = sf.update_open_orders(orderIDList.json())
        oBook = sf.get_order_book(stock)

        BestAsk = sf.read_orderbook(oBook, "asks", "price", 1)
        BestBid = sf.read_orderbook(oBook, "bids", "price", 1)
        q_bid = min(sf.read_orderbook(oBook, "bids", "qty", 1), 250)  # min of 250 because we only have 1000 on either side of pos to work with.
        q_ask = min(sf.read_orderbook(oBook, "asks", "qty", 1), 250)
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
     
        nav = sf.cash + sf.positionSoFar * sf.get_quote(stock).get("last") * (.01)
        print "T%d, Best Ask %r , Best Bid %r, average %r" % \
            ((end - start), BestAsk, BestBid, ma_20)

        if buy_condition(Spread, sf.expectedPosition):
            buyOrder = sf.make_order(BestBid, q_bid, stock, "buy", "limit")
            buyPrice = buyOrder.get('price')
            buyID = buyOrder.get('id')
            print "\tplaced buy ord. - %d units at %d ID %d" % (q_bid, buyPrice, buyID)
        
        if sell_condition(Spread, sf.expectedPosition):
            sellOrder = sf.make_order(int(BestAsk * premium), q_ask, stock, "sell", "limit")
            sellPrice = sellOrder.get('price')
            sellID = sellOrder.get('id')
        
            print "\tplaced sold ord. - %d units at %d ID %d" % (q_ask, sellPrice, sellID)

        end = time.time()
        orderIDList = sf.status_for_all_orders_in_stock(stock)
        identify_unfilled_orders(orderIDList.json(), should_cancel_unfilled)
        time.sleep(2)  # slow things down a bit, because we are querying the same information.
except KeyboardInterrupt:
    print "ctrl+c pressed!"
    with open("results.txt", "w") as EndLog:
        json.dump(orderIDList, EndLog)
    EndLog.close()
