"""
testing Multi Thread.
FourthTrade will be separated by two thread
1st Thread. -> Buy / Sell
    i.)     buy and sell while NAV is less than $250000
    ii.)    wait a sec, check NAV status.
    iii.)   repeat.
2nd Thread -> Read through open order and cancel unfilled
    i.)     check the order list for open orders.
3rd Thread -> Current Status-> prints out what is the current NAV, Position, Expected Position etc.

due to the internal waits in the Queue library for get and put. we dont need to compensate with
our own time.wait in our own script.
"""
from __future__ import division
import threading
import gamemaster
import time
import Queue  # Queue encapsulates ideas of wait() , notify() , acquire() for multithread use


status_queue = Queue.Queue(maxsize=0)  # maxsize = 0 -> queue size is infinite.
gameOn = True

class CurrentStatus:
    """is now separated from BuySell. runs and update
    positionSoFar, cash, expectedPosition, NAV. AKA the producer thread.
    """
    
    def __init__(self, stockfighter):
        print "Initializing CurrentStatus..."
        self.sf = stockfighter
        self.start = time.time()

    def run(self):
        stock = self.sf.tickers
        tempI = 0  # i use this to check whether the info pass on to the status_queue is the same as the one read on BuySell.
        global status_queue
        global gameOn
        while gameOn:
            time.sleep(3)    # slow things down a bit, because we are querying the same information.
            orders = self.sf.status_for_all_orders_in_stock(stock)
            positionSoFar, cash, expectedPosition = self.sf.update_open_orders(orders)
            
            last = self.sf.get_quote(stock).get("last")
            if last is None:
                last = 0
            nav = cash + positionSoFar * last * (.01)
            status_queue.put([cash, expectedPosition, nav, tempI])
            nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below
            print "----\nT%d approximate Pos. %d, Expected Pos. %d, Cash %d, NAV %s" % \
                  ((time.time() - self.start), positionSoFar, expectedPosition, cash, nav_currency),
            # print "temp %d" % (tempI)
            tempI += 1


class BuySell:
    
    def __init__(self, stockfighter):
        print "Initializing BuySell..."
        self.sf = stockfighter
        self.start = time.time()

    def buy_condition(self, tExpectedPosition, positionSoFar, tBestBid, tMA):
        """to be tailored for each level.
            will buy if the price is not above MA20 price.
        """
        if tBestBid > 0 and tExpectedPosition <= 500 and positionSoFar <= 500 and tBestBid < tMA:
            return True

    def sell_condition(self, tExpectedPosition, positionSoFar, tBestAsk, tMA):
        """to be tailored for each level.
            will sell if the price is not below MA20 price.
        """
        if tBestAsk > 0 and tExpectedPosition >= -500 and positionSoFar >= -500 and tBestAsk > tMA:
            return True
     
    def run(self):
        ma_20_list = []         # moving average 20 lets the script know current trend.
        ma_20 = 0
        gapPercent = .02        # how much different in % each order will be
        worstCase = .04         # how much different the best offer and worst offer will be
        stock = self.sf.tickers
        global status_queue
        global gameOn
        # global quote_queue
        positionSoFar = 0
        nav = 0
        try:
            while nav < 250000 and sf.heartbeat():
                if abs(positionSoFar) > 1000:
                    gameOn = False
                    break

                oBook = self.sf.get_order_book(stock)
                # will multiply base on the below info with gapPercent
                bestAsk = self.sf.read_orderbook(oBook, "asks", "price", 1)
                bestBid = self.sf.read_orderbook(oBook, "bids", "price", 1)
                q_bid = min(self.sf.read_orderbook(oBook, "bids", "qty", 1), 100)
                q_ask = min(self.sf.read_orderbook(oBook, "asks", "qty", 1), 100)
                discount = .02
                if len(ma_20_list) > 20:  # Moving average 20 ticks
                    ma_20_list.pop(0)
                
                ma_20_list.append(self.sf.get_quote(stock).get("last"))
                ma_20 = sum(ma_20_list) / len(ma_20_list)
                             
                cash, expectedPosition, nav, tempII = status_queue.get()
                positionSoFar = sf.positionSoFar  # the sf.positionSoFar is updated by the execution thread. much faster
                print "\nB_Bid %d, B_Ask %d Last %d, average %d" % (bestBid, bestAsk, ma_20_list[-1], ma_20),
                # print "temp %d" % (tempII)

                if self.buy_condition(expectedPosition, positionSoFar, bestBid, ma_20):
                    # loop through make multiple bids.
                    increment = int(bestBid * gapPercent * -1)
                    worstBid = int(bestBid * (1 - worstCase))
                    q_max = 999 - max(expectedPosition, positionSoFar)  # this is the max amount i can bid without game over.
                    q_actual = int(abs(q_max * .5))
                    # orderType = "limit"
                    orderType = "limit"
                    actualBid = bestBid

                    for actualBid in range(bestBid, worstBid, increment):
                        buyOrder = sf.make_order(int(actualBid * (1 + discount)), q_actual, stock, "buy", orderType)                        
                        print "\n\tBBBBB placed  buy ord. +%d units at %d ID %r %r" % (q_actual, buyOrder.get('price'),
                                                                                       buyOrder.get('id'), orderType)
                        q_actual = int(abs(q_max * .25))
                        orderType = "immediate-or-cancel"
                        expectedPosition += q_actual
                """Bug. after we make a series of buy orders. our expectedPosition should change appropriately.
                but right now it's not. there should be a line here that updates the expectedsofar variable
                locally before moving on to the sell condition.
                """

                positionSoFar = sf.positionSoFar
                if self.sell_condition(expectedPosition, positionSoFar, bestAsk, ma_20):
                    # loop through make multiple asks.
                    increment = int(bestAsk * gapPercent)
                    worstAsk = int(bestAsk * (1 + worstCase))
                    q_max = -999 - min(expectedPosition, positionSoFar)  # this is the max amount i can bid without game over.
                    q_actual = int(abs(q_max * .5))
                    # orderType = "limit"
                    orderType = "limit"
                    actualAsk = bestAsk
                    for actualAsk in range(bestAsk, worstAsk, increment):
                        # print "actual ask %r and q_actual %r" %(actualAsk, q_actual)
                        sellOrder = sf.make_order(int(actualAsk * (1 - discount)), q_actual, stock, "sell", orderType)                        
                        print "\n\tSSSSS placed  sell ord. -%d units at %d ID %r %r" % (q_actual, sellOrder.get('price'),
                                                                                        sellOrder.get('id'), orderType)
                        q_actual = int(abs(q_max * .25))
                        orderType = "immediate-or-cancel"

            print "BuySell Closed, final values Nav. %d Positions. %d" % (nav, positionSoFar)            
            gameOn = False
        except KeyboardInterrupt:
            print "ctrl+c pressed! leaving buy sell"
            gameOn = False

class CheckFill:
    
    def __init__(self, stockfighter):
        print "Initializing CheckFill.."
        self.sf = stockfighter
        self.stock = self.sf.tickers
        self.timeToWait = 3     # for how long the unfill orders can last.

    def identify_unfilled_orders(self, orderList, callback):
        """check through orderIDlist, and return a list of
        orders that is not gonna be filled at the moment because
        the price is out the money.
        """
        for y in orderList:
            x = orderList[y]
            if x["open"]:
                if callback(x):
                    print "\n\tCancelling %s %s units at %s ID %s" % (x["direction"], x["qty"], x["price"], x["id"])
                    self.sf.delete_order(self.stock, x["id"])

    def should_cancel_unfilled(self, order):
        """if this order is out of money, or outstanding too long then cancel it. but only if
        cancelling the order doesn't drive the expectedPosition out of the allowable range.
        """
        oBook = self.sf.get_order_book(self.stock)
        s_BestAsk = self.sf.read_orderbook(oBook, "asks", "price", 1)
        s_BestBid = self.sf.read_orderbook(oBook, "bids", "price", 1)
        price = order["price"]

        if order["direction"] == "buy":
            diff = (s_BestBid - price) / price * 1.0
            # print "\nJudging Buy order %d, s_BestBid %d, Price %d,  diff is %r, expectedPosition %d, and order qty is %d" % (order['id'], s_BestBid, price, 
            #                                                                                                                  diff, sf.expectedPosition, order['qty'])
            if (diff < -.03 or diff > .15) and -1000 < (sf.expectedPosition - order['qty']) < 1000:
                return True
  
        else:
            diff = (s_BestAsk - price) / price * 1.0
            if (diff > .03 or diff < -.15) and -1000 < (sf.expectedPosition - (order['qty'] * -1)) < 1000:
                # print "\nJudging Sell order%d, diff is %r, expectedPosition %d, and order qty is %d" % (order['id'], diff, sf.expectedPosition, order['qty'])
                return True
        return False

    def run(self):
        global gameOn
        try:
            while gameOn:
                time.sleep(1)
                orders = self.sf.status_for_all_orders_in_stock(self.stock)
                self.identify_unfilled_orders(orders, self.should_cancel_unfilled)
        except KeyboardInterrupt:
            print "ctrl+c pressed! leaving checking fills"

if __name__ == '__main__':
    
    sf = gamemaster.StockFighter("sell_side")
    bs = BuySell(sf)
    cf = CheckFill(sf)
    cs = CurrentStatus(sf)

    bsThread = threading.Thread(target=bs.run, args=())
    cfThread = threading.Thread(target=cf.run, args=())
    csThread = threading.Thread(target=cs.run, args=())
    bsThread.daemon = True  # this allows the thread to exit without waiting for it to finish executing.
    cfThread.daemon = True
    csThread.daemon = True
    bsThread.start()
    cfThread.start()
    csThread.start()

    try: 
        while gameOn and sf.heartbeat():          
            time.sleep(1)
    except KeyboardInterrupt:
        print "ctrl+c pressed! leaving FourthTradeMT"
    finally:
        printGraph = raw_input("Would you like to chart this level? y/n ")
        if printGraph.upper() == 'Y':
            sf.make_graphs()

       