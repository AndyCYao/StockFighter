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

positionSoFar = 0  # if negative means short if positive long
premium = 1.025
ma_20_list = []    # moving average 20 lets the script know current trend.
ma_20 = 0
nav = 0

def buy_condition(tSpread, tPositionSoFar):
    """to be tailored for each level"""
    if tSpread > 0.005 and tPositionSoFar <= 0:
        return True
    return False

def sell_condition(tSpread, tPositionSoFar):
    """to be tailored for each level"""
    if tSpread > 0.005 and tPositionSoFar >= 0:
        return True
    return False

# while (end - start) < 120:
while nav < 12000:
    orderIDList = sf.status_for_all_orders_in_stock(stock)
    positionSoFar, cash = sf.update_open_orders(orderIDList.json())
    oBook = sf.get_order_book(stock)

    BestAsk = sf.read_orderbook(oBook, "asks", "price")
    BestBid = sf.read_orderbook(oBook, "bids", "price")
    q_bid = min(sf.read_orderbook(oBook, "bids", "qty"),250) #min of 250 because we only have 1000 on either side of pos to work with.
    q_ask = min(sf.read_orderbook(oBook,"asks","qty"),250)

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
    
    print "T%d Pos. %d Best Ask %r , Best Bid %r, Spread %r, average %r, NAV %s" % \
        ((end - start), positionSoFar, BestAsk, BestBid, Spread, ma_20, nav_currency)

    time.sleep(1)

    if buy_condition(Spread, positionSoFar):    
        buyOrder = sf.make_order(BestBid, q_bid, stock, "buy", "limit")
        buyPrice = buyOrder.get('price')
        buyID = buyOrder.get('id')
        print "placed buy ord. - %d units at %d ID %d" % (q_bid, buyPrice, buyID)
    
    if sell_condition(Spread, positionSoFar):
        sellOrder = sf.make_order(int(BestAsk * premium), q_ask, stock, "sell", "limit")
        sellPrice = sellOrder.get('price')
        sellID = sellOrder.get('id')
    
        print "placed sold ord. - %d units at %d ID %d" % (q_ask, sellPrice, sellID)

    end = time.time()

