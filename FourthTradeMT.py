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
            time.sleep(1.5)    # slow things down a bit, because we are querying the same information.
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
        self.stock = self.sf.tickers

    def find_ordered(self, direction):
        """        
        find the maximum q we can order in either direction.
        This looks at all open order of that direction and tally their qty.
        """
        orders_list = self.sf.status_for_all_orders_in_stock(self.stock)
        already_order = 0
        for x in orders_list:
            o = orders_list[x]
            # if o["open"] and o["direction"] == direction:
            if o["direction"] == direction and o['qty'] != 0:
                print "id: %d %r qty %d " % (o['id'], o['direction'], o['qty'])
                already_order += o['qty']
        return already_order   

    def buy_condition(self, tExpectedPosition, positionSoFar, tBestBid, tMA):
        """to be tailored for each level.
            will buy if the price is not above MA20 price. and current open order qtys + positionSoFar < 1000 for buy
        """        
        already_bought = self.find_ordered("buy")
        # basically we want 
        #  1000 => positionSoFar +  already bought + to be ordered aka q_max
        # q_max = 1000 - max(tExpectedPosition, positionSoFar)  # this is the max amount i can bid without game over.
        q_max = 1000 - positionSoFar - already_bought
        print "\n\tIn BuyCond. tBestBid %r, ma %r 1000 - positionSoFar %r - already_bought %r = q_max %r can buy?" % (tBestBid, tMA, positionSoFar, already_bought, q_max),
        if 0 < tBestBid < tMA and q_max > 4 and already_bought + positionSoFar < 1000:  # q_max > 4 because we still want reasonable bid quantity per each order
            print "..yes"
            return True
        print "..no"

    def sell_condition(self, tExpectedPosition, positionSoFar, tBestAsk, tMA):
        """to be tailored for each level.
            will sell if the price is not below MA20 price. and current open order + positionSoFar > -1000 for sell
        """
        already_sold = self.find_ordered("sell") * -1
        # q_max = abs(-1000 - min(tExpectedPosition, positionSoFar))
        # we want -1000 >= positionSoFar + already_sold + To be ordered aka q_max
        q_max = abs(-1000 - positionSoFar - already_sold)
        print "\n\tIn SellCond. tBestAsk %r,ma %r -1000 - positionSoFar %r - already_sold %r = q_max %r can sell?" % (tBestAsk, tMA, positionSoFar, already_sold, q_max),
        if tBestAsk > tMA and q_max > 4 and already_sold + positionSoFar > -1000:
            print "..yes"
            return True
        print "..no"

    def run(self):
        ma_20_list = []         # moving average 20 lets the script know current trend.
        ma_20 = 0
        gapPercent = .02        # how much different in % each order will be
        worstCase = .04         # how much different the best offer and worst offer will be
        global status_queue
        global gameOn
        positionSoFar = 0
        nav = 0
        try:
            while nav < 250000 and self.sf.heartbeat():
                if abs(self.sf.positionSoFar) > 1000:
                    gameOn = False
                    break

                oBook = self.sf.get_order_book(self.stock)
                # will multiply base on the below info with gapPercent
                bestAsk = self.sf.read_orderbook(oBook, "asks", "price", 1)
                bestBid = self.sf.read_orderbook(oBook, "bids", "price", 1)
                discount = .01
                if len(ma_20_list) > 20:  # Moving average 20 ticks
                    ma_20_list.pop(0)
                
                ma_20_list.append(self.sf.get_quote(self.stock).get("last"))
                ma_20 = sum(ma_20_list) / len(ma_20_list)
                             
                cash, expectedPosition, nav, tempII = status_queue.get()
                positionSoFar = self.sf.positionSoFar  # the sf.positionSoFar is updated by the execution thread. much faster
                # print "\nB_Bid %d, B_Ask %d Last %d, average %d" % (bestBid, bestAsk, ma_20_list[-1], ma_20),
                # print "temp %d" % (tempII)

                if self.buy_condition(expectedPosition, positionSoFar, bestBid, ma_20):
                    # loop through make multiple bids.
                    increment = int(bestBid * gapPercent * -1)
                    worstBid = int(bestBid * (1 - worstCase))
                    already_bought = self.find_ordered("buy")  # this is the max amount i can bid without game over.
                    q_max = 1000 - positionSoFar - already_bought
                    q_actual = int(abs(q_max * .5))
                    orderType = "limit"
                    actualBid = bestBid

                    for actualBid in range(bestBid, worstBid, increment):
                        buyOrder = sf.make_order(int(actualBid * (1 + discount)), q_actual, self.stock, "buy", orderType)                        
                        print "\n\tPlaced BUY ord. id:%r +%r units @ %r %r time ordered %r" % (buyOrder.get('id'), q_actual, 
                                                                                               buyOrder.get('price'), orderType,
                                                                                               buyOrder.get('ts')[buyOrder.get('ts').index('T'):])
                        q_actual = int(abs(q_max * .25))
                        orderType = "immediate-or-cancel"
                        expectedPosition += q_actual
                
                positionSoFar = self.sf.positionSoFar

                if self.sell_condition(expectedPosition, positionSoFar, bestAsk, ma_20):
                    # loop through make multiple asks.
                    increment = int(bestAsk * gapPercent)
                    worstAsk = int(bestAsk * (1 + worstCase))
                    already_sold = self.find_ordered("sell") * -1       
                    # q_max = abs(-1000 - min(tExpectedPosition, positionSoFar))
                    # we want -1000 >= positionSoFar + already_sold + To be ordered aka q_max
                    q_max = abs(-1000 - positionSoFar - already_sold)
                    q_actual = int(q_max * .5)
                    orderType = "limit"
                    actualAsk = bestAsk
                    for actualAsk in range(bestAsk, worstAsk, increment):
                        # print "actual ask %r and q_actual %r" %(actualAsk, q_actual)
                        sellOrder = sf.make_order(int(actualAsk * (1 - discount)), q_actual, self.stock, "sell", orderType)                        
                        print "\n\tPlaced SELL ord. id:%r -%r units @ %r %r time ordered %r" % (sellOrder.get('id'), q_actual, 
                                                                                                sellOrder.get('price'), orderType,
                                                                                                sellOrder.get('ts')[sellOrder.get('ts').index('T'):])
                        q_actual = int(q_max * .25)
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
                # print "\n%r" %(x)
                if callback(x):
                    print "\n\tCancelling %s id:%r units %d @ %d" % (x["direction"], x["id"], x["qty"], x["price"])
                    self.sf.delete_order(self.stock, x["id"])
                    
    def should_cancel_unfilled(self, order):
        """if this order is out of money, or outstanding too long then cancel it. but only if
        cancelling the order doesn't drive the expectedPosition out of the allowable range.
        """
        oBook = self.sf.get_order_book(self.stock)
        s_BestAsk = self.sf.read_orderbook(oBook, "asks", "price", 1)
        s_BestBid = self.sf.read_orderbook(oBook, "bids", "price", 1)
        price = order["price"]
        if s_BestAsk == 0:
            s_BestAsk = price
        if s_BestBid == 0:
            s_BestBid = price

        if order["direction"] == "buy":
            diff = (s_BestBid - price) / price * 1.0
            """
            print "\nJudging Buy order %d, s_BestBid %d, Price %d,  diff is %r, expectedPosition %d, and order qty is %d" % (order['id'], s_BestBid, price, 
                                                                                                                             diff, self.sf.expectedPosition, order['qty'])
            """
            if (diff < -.03 or diff > .15) and -1000 < (self.sf.expectedPosition - order['qty']) < 1000:
                return True
  
        else:
            diff = (s_BestAsk - price) / price * 1.0
            """
            print "\nJudging Sell order%d, s_BestAsk %r, Price %r,diff is %r, expectedPosition %d, and order qty is %d" % (order['id'], s_BestAsk, price, 
                                                                                                                           diff, self.sf.expectedPosition, order['qty'])
            """
            if (diff > .03 or diff < -.15) and -1000 < (self.sf.expectedPosition - (order['qty'] * -1)) < 1000:
                return True
        return False

    def run(self):
        global gameOn
        try:
            while gameOn:
                time.sleep(2)
                orders = self.sf.status_for_all_orders_in_stock(self.stock)
                self.identify_unfilled_orders(orders, self.should_cancel_unfilled)
        except KeyboardInterrupt:
            print "ctrl+c pressed! leaving checking fills"

if __name__ == '__main__':
    
    sf = gamemaster.StockFighter("dueling_bulldozers")
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
