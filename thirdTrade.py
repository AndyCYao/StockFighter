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
"""

import gamemaster
import time

start = time.time()
end = time.time()


sf = gamemaster.StockFighter("sell_side")
stock = sf.tickers

# orderIDList = {}
positionSoFar = 0  # if negative means short if positive long
premium = 1.025
ma_20_list = []    # moving average 20 lets the script know current trend.
ma_20 = 0
nav = 0
# while (end - start) < 120:
while nav < 15000:
    time.sleep(2)

    if len(ma_20_list) > 20:  # if theres stuff in ma_20_list
        ma_20_list.pop(0)
    ma_20_list.append(sf.get_quote(stock).get("last"))
    curr_count = len(ma_20_list)
    for x in ma_20_list:
        print x,
        ma_20 += x + 0.0
    ma_20 = int(ma_20 / curr_count)
    orderIDList = sf.status_for_all_orders_in_stock(stock)
    positionSoFar, cash = sf.update_open_orders(orderIDList.json())
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

    if Spread > 0.005 and abs(positionSoFar) < 500:  # making a transaction
        buyOrder = sf.make_order(BestBid, q, stock, "buy", "limit")
        sellOrder = sf.make_order(int(BestAsk * premium), q, stock, "sell", "limit")
        # print "Print Buy Order %s" % (buyOrder)
        buyID = buyOrder.get('id')
        sellID = sellOrder.get('id')
        # orderIDList[buyID] = 0      # add buy order ID to orderlist
        # orderIDList[sellID] = 0     # do same for sell

        buyPrice = buyOrder.get('price')
        sellPrice = sellOrder.get('price')
        print "Bought %d at %d ID %d - Sold at %d ID %d" % (q, buyPrice, buyID,
                sellPrice, sellID)

    print 'Waiting for keyboard interrupt'
    try:
        while True:
            time.sleep(1)
            end = time.time()
            orderIDList = sf.status_for_all_orders_in_stock(stock)
            positionSoFar, cash = sf.update_open_orders(orderIDList.json())
            nav = cash + positionSoFar * sf.get_quote(stock).get("last") * (.01)
            nav_currency = '${:,.2f}'.format(nav)
            print "T%d cur. Cash %d - Pos %d - NAV %r" % ((end-start), cash, 
                positionSoFar, nav_currency)
    except KeyboardInterrupt:
        print "Keyboard Pressed!"
        continue

