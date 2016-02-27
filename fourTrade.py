"""
Feb 25th 2016 Fourth Trade Duelling BullDozers.

"""

import gamemaster
import time

start = time.time()
end = time.time()


sf = gamemaster.StockFighter("dueling_bulldozers")
stock = sf.tickers

orderIDList = {}
positionSoFar = 0  # if negative means short if positive long
premium = 1.025
ma_20_list = []    # moving average 20 lets the script know current trend.
ma_20 = 0
while (end - start) < 50:
    time.sleep(2)

    if len(ma_20_list) > 20:  # if theres stuff in ma_20_list
        ma_20_list.pop(0)
    ma_20_list.append(sf.get_quote(stock).get("last"))
    curr_count = len(ma_20_list)
    for x in ma_20_list:
        # print x,
        ma_20 += x + 0.0
    ma_20 = int(ma_20 / curr_count)
    positionSoFar = sf.update_open_orders(orderIDList)
    oBook = sf.get_order_book(stock)

    BestAsk = sf.read_orderbook(oBook, "asks", "price")
    BestBid = sf.read_orderbook(oBook, "bids", "price")
    q = sf.read_orderbook(oBook, "bids", "qty")
    if q > 250:         # i can only handle +- 1000 maximum so less risk
        q = 250

    Difference = BestAsk - BestBid

    try:
        if BestBid > 0:
            Spread = "{0:%}".format(Difference / (BestAsk + 0.0))
        else:
            Spread = 0
    except ZeroDivisionError:
        Spread = 0

    end = time.time()
    print "T%d Pos. %d Best Ask %r , Best Bid %r, q %r Spread %r, average %r" % \
        ((end - start), positionSoFar, BestAsk, BestBid, q, Spread, ma_20)

    if Spread > .005 and abs(positionSoFar) < 500:  # making a transaction

        buyOrder = sf.make_order(BestBid, q, stock, "buy", "limit")
        sellOrder = sf.make_order(int(BestAsk * premium), q, stock, "sell", "limit")
        # print "Print Buy Order %s" % (buyOrder)
        buyID = buyOrder.get('id')
        sellID = sellOrder.get('id')
        orderIDList[buyID] = 0      # add buy order ID to orderlist
        orderIDList[sellID] = 0     # do same for sell

        buyPrice = buyOrder.get('price')
        sellPrice = sellOrder.get('price')
        print "Bought %d at %d ID %d - Sold at %d ID %d" % (q, buyPrice, buyID,
                sellPrice, sellID)

    # try:
    """
    print 'Waiting for keyboard interrupt'
    while True:
        try:
            time.sleep(1)
            end = time.time()
            positionSoFar = sf.update_open_orders(orderIDList)
            print "cur. position %d" % (positionSoFar)
        except KeyboardInterrupt:
            print "Keyboard Pressed!"
    """
