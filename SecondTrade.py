import gamemaster
import time
import datetime
import random

start = time.time()
end = time.time()
totalGoal = 100000
positionSoFar = 0

sf = gamemaster.StockFighter("chock_a_block")
# sf = gamemaster.StockFighter.test_mode()
stock = sf.tickers
orders = {} # Execution Socket will populate this dictionary.

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
"""
def ExecutionSocket(m):
    currentPos = 0
    currentPosCash = 0
    expectedPos = 0
    global orders
    print "\n***** IN websocket ****"
    
    if m is not None:
        orders[m["standingId"]] = m
        
        for x in orders:
            o = orders[x]
            direction = o["order"]["direction"]
            totalFilled = o["order"]["totalFilled"]
            price = o["order"]["price"]
            qty = o["order"]["qty"] + totalFilled
            
            if direction == "sell":
                totalFilled = totalFilled * -1
                qty = qty * -1
            
            currentPos += totalFilled
            expectedPos += qty
                # -.01 because we are getting the correct unit
            currentPosCash += totalFilled * price * (-.01)        
            
        
        print "EXECUTION current pos is %d and $%d" %(currentPos, currentPosCash)
        # return currentPos, currentPosCash, expectedPos
 
    else:
        print "...restarting websocket..."
        sf.execution_venue_ticker(ExecutionSocket)
"""

sf.execution_venue_ticker(sf.execution_socket)
while totalGoal > positionSoFar and sf.heartbeat():
    randSleep = random.randint(1,3)
    time.sleep(randSleep)
    oBook = sf.get_order_book(stock)
    bestBid = sf.read_orderbook(oBook, "bids", "price", 1 ) + 1
    q_ask = sf.read_orderbook(oBook, "asks", "qty", 1)
    q_ask_actual = int(q_ask * .6)  # i am ordering 20% of actual quote because dont want to affect market.
    
    if q_ask_actual:

        # loop through the gapPercent and make multiple bids.
        increment = int(bestBid * .01 * -1)
        worstBid = int(bestBid * (1 - .03))
        q_increment = int(q_ask_actual* .01)
        q_actual = q_ask_actual
        # print q_actual, bestBid, worstBid, increment
        for actualBid in range(bestBid, worstBid, increment):
            
            buyOrder = sf.make_order(actualBid, q_actual, stock, "buy", "limit")
            print "\n\tBBBBB placed buy ord. +%d units at %d ID %d" % (q_actual, buyOrder.get('price'),
                                                                        buyOrder.get('id'))
            q_actual -= q_increment

    orderIDList = sf.status_for_all_orders_in_stock(stock)
    positionSoFar, cash, expectedPosition = sf.update_open_orders(orderIDList)
    end = time.time()
    identify_unfilled_orders(orderIDList.json(), should_cancel_unfilled)
    print "T%d Actual Pos. %d" % ((end - start), positionSoFar)
