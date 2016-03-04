import gamemaster
import time

start = time.time()
end = time.time()
totalGoal = 100000
positionSoFar = 0

sf = gamemaster.StockFighter("chock_a_block")
stock = sf.tickers

while totalGoal > positionSoFar and (end - start) < 120:

    time.sleep(5)
    oBook = sf.get_order_book(stock)
    BestAsk = sf.read_orderbook(oBook, "asks", "price")
    BestBid = sf.read_orderbook(oBook, "bids", "price") + 5  # always pay more than next guy to win the bid.
    q_ask = sf.read_orderbook(oBook, "asks", "qty")
    q_ask_actual = int(q_ask * .2)  # i am ordering 20% of actual quote because dont want to affect market.
    
    if q_ask:
        buyOrder = sf.make_order(BestBid, q_ask_actual, stock, "buy", "limit")
        buyID = buyOrder.get('id')
        buyPrice = buyOrder.get('price')
        print "\t placed buy order at ID %s %s units" % (buyID, q_ask_actual)
    
    orderIDList = sf.status_for_all_orders_in_stock(stock)
    positionSoFar, cash, expectedPosition = sf.update_open_orders(orderIDList.json())
    end = time.time()
    print "T%d Actual Pos. %d" % ((end - start), positionSoFar)

