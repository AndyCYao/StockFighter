"""Feb 25th 2016 Third Trade sell_side."""
# from __future__ import division
import gamemaster
import time

start = time.time()
end = time.time()


sf = gamemaster.StockFighter("sell_side")
stock = sf.tickers

orderIDList = {}
positionSoFar = 0  # if negative means short if positive long

while (end - start) < 60:

    time.sleep(1)
    positionSoFar = sf.update_open_orders(orderIDList)
    oBook = sf.get_order_book(stock)

    BestAsk = sf.read_orderbook(oBook, "asks", "price")
    BestBid = sf.read_orderbook(oBook, "bids", "price")
    q = sf.read_orderbook(oBook, "bids", "qty")
    Difference = BestAsk - BestBid

    try:
        Spread = "{0:%}".format(Difference / (BestAsk + 0.0))
    except ZeroDivisionError:
        Spread = 0

    end = time.time()
    print "Pos. %d Best Ask %r , Best Bid %r, q %r Spread %r  Time - %d" % \
        (positionSoFar, BestAsk, BestBid, q, Spread, (end - start))
    


    if Spread > 0.005 and abs(positionSoFar) < 500:  # making a transaction
        buyOrder = sf.make_order(BestBid, q, stock, "buy", "limit")
        sellOrder = sf.make_order(BestAsk, q, stock, "sell", "limit")
        # print "Print Buy Order %s" % (buyOrder)
        buyID = buyOrder.get('id')
        sellID = sellOrder.get('id')
        orderIDList[buyID] = 0      # add buy order ID to orderlist
        orderIDList[sellID] = 0     # do same for sell

        buyPrice = buyOrder.get('price')
        sellPrice = sellOrder.get('price')
        print "Bought at %d ID %d - Sold at %d ID %d" % (buyPrice, buyID,
                sellPrice, sellID)

    try:
        print 'Waiting for keyboard interrupt'
        while True:
            time.sleep(2)
            positionSoFar = sf.update_open_orders(orderIDList)            
    except KeyboardInterrupt:
        pass
