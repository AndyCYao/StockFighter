import requests
import json
import gamemaster
import time

start = time.time()
end  = time.time()
totalGoal = 100000

sf = gamemaster.StockFighter("chock_a_block")
stock = sf.tickers

while totalGoal > 0 and (end - start) < 120:

    time.sleep(5)
    oBook = sf.get_order_book(stock)
    BestAsk , q = sf.return_best_price(oBook) # best asking price
    buyOrder = sf.buy_stock(BestAsk,q,stock)
    # print "Print Buy Order %s" %(buyOrder)
    buyID = buyOrder.get('id')
    buyPrice = buyOrder.get('price')
    print "check fill status - ID %s" %(buyID)
    
    fillResults = sf.fill_confirmation(stock,buyID)
    if fillResults:
        totalGoal -= q
        print "bought at %s - remaining to buy %s" %(buyPrice, totalGoal)
    
    end  = time.time()
    print "%s -- confirmed fill - %s " %(end - start,fillResults)

