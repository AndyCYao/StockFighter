import gamemaster
import time
import datetime
import Queue  # Queue encapsulates ideas of wait() , notify() , acquire() for multithread use

if __name__ == '__main__':
    
    sf = gamemaster.StockFighter.test_mode()
    print "trying new status for all orders in stock..",
    sf.status_for_all_orders_in_stock(sf.tickers)
    try:
        while 1:
            print "waiting for keyboard interrupt"
            time.sleep(4)               # the market bots sleep for 4 sec and make a trade
    except KeyboardInterrupt:
        print "ctrl+c pressed! leaving"
