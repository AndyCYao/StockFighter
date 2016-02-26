"""Feb 25th 2016 Third Trade sell_side."""
# from __future__ import division
import gamemaster
import time

start = time.time()
end = time.time()


sf = gamemaster.StockFighter("sell_side")
stock = sf.tickers

orderIDList = []
positionSoFar = 0  # if negative means short if positive long

while (end - start) < 100:

    time.sleep(1)

    for x in orderIDList:
        num, direction, state = sf.fill_confirmation(stock, x)
        if direction == "sell":
            positionSoFar -= num
        else:
            positionSoFar += num
        if state is False:  # meaning this is closed
            orderIDList.pop(orderIDList.index(x))

    oBook = sf.get_order_book(stock)

    BestAsk = sf.read_orderbook(oBook, "asks", "price")
    BestBid = sf.read_orderbook(oBook, "bids", "price")
    q = sf.read_orderbook(oBook, "bids", "qty")
    Difference = BestAsk - BestBid

    try:
        Spread = Difference / (BestAsk + 0.0)
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
        orderIDList.append(buyID)
        orderIDList.append(sellID)

        buyPrice = buyOrder.get('price')
        sellPrice = sellOrder.get('price')
        print "Bought at %d ID %d - Sold at %d ID %d" % (buyPrice, buyID,
                sellPrice, sellID)

    """
    fillResults = sf.fill_confirmation(stock, buyID)
    if fillResults:
        print "bought at %s " % (buyPrice)
    """
