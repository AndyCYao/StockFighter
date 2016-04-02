import gamemaster
import time
import datetime

start = time.time()
end = time.time()
totalGoal = 100000


sf = gamemaster.StockFighter("chock_a_block")
# sf = gamemaster.StockFighter.test_mode()
stock = sf.tickers

def identify_unfilled_orders(orderList, callback):
        """check through orderIDlist, and return a list of
        orders that is not gonna be filled at the moment because
        the price is out the money.
        """
        for y in orderList:
            x = orderList[y]
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

sf.execution_venue_ticker(sf.execution_socket)
while totalGoal > sf.positionSoFar and sf.heartbeat():
    oBook = sf.get_order_book(stock)
    bestBid = sf.read_orderbook(oBook, "bids", "price", 1) + 1
    q_ask = sf.read_orderbook(oBook, "asks", "qty", 1)
    q_ask_actual = min(int(q_ask * .6), 500)  # i am ordering 20% of actual quote because dont want to affect market.
    
    if q_ask_actual:

        # loop through the gapPercent and make multiple bids.
        increment = int(bestBid * .01 * -1)
        worstBid = int(bestBid * (1 - .03))
        q_increment = int(q_ask_actual * .2)
        q_actual = q_ask_actual
        # print q_actual, bestBid, worstBid, increment
        for actualBid in range(bestBid, worstBid, increment):
            
            buyOrder = sf.make_order(actualBid, q_actual, stock, "buy", "limit")
            print "\n\tBBBBB placed buy ord. +%d units at %d ID %d" % (q_actual, buyOrder.get('price'),
                                                                       buyOrder.get('id'))
            q_actual -= q_increment

    end = time.time()
    sf.order = sf.status_for_all_orders_in_stock(stock)
    positionSoFar, cash, expectedPosition = sf.update_open_orders(sf.order)
    print "T%d Aprrox.. actual Pos. %d - expected Pos. %d" % ((end - start), positionSoFar, expectedPosition)
    identify_unfilled_orders(sf.order, should_cancel_unfilled)
    time.sleep(3)
