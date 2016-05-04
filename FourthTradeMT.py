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
"""
import threading
import gamemaster
import time
# import Queue  # Queue encapsulates ideas of wait() , notify() , acquire() for multithread use


# status_queue = Queue.Queue(maxsize=0)  # maxsize = 0 -> queue size is infinite.
gameOn = True


class CurrentStatus:
    """Print out the status of this run.

    Print out the time elapse, positionSoFar, expectedPosition, cash, nav
    """
    
    def __init__(self, stockfighter):
        print "Initializing CurrentStatus..."
        self.sf = stockfighter
        self.start = time.time()
        self.timeToSleep = 1.5

    def run(self):
        stock = self.sf.tickers
        global gameOn
        while gameOn:
            time.sleep(self.timeToSleep)    # slow things down a bit, because we are querying the same information.
            orders = self.sf.status_for_all_orders_in_stock(stock)
            positionSoFar, cash, expectedPosition = self.sf.update_open_orders(orders)
            
            last = self.sf.get_quote(stock).get("last")
            if last is None:
                last = 0
            nav = cash + positionSoFar * last * (.01)
            nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below
            print "----\nT%d approximate Pos. %d, Expected Pos. %d, Cash %d, NAV %s" % \
                  ((time.time() - self.start), positionSoFar, expectedPosition, cash, nav_currency),


class BuySell:

    def __init__(self, stockfighter):
        print "Initializing BuySell..."
        self.sf = stockfighter
        self.start = time.time()
        self.stock = self.sf.tickers
        self.order_limit = 1000  # we can go +/- in this range. the game officially has 1000 but since my codes suck i will use 1000 to accomodate the error.
        self.threshold = 200  # this is the qty i want to cross before placing order, otherwise im flooding too much tiny orders 
        self.gap_percent = .02
        self.worst_case = .04

    def find_ordered(self, direction):
        """find the maximum q we can order in either direction.
        
        This looks at all open order of that direction and tally their qty.
        """
        already_order = 0
        for x in self.sf.orders:
            o = self.sf.orders[x]
            if o["direction"] == direction and o['qty'] != 0:
                # print "id: %d %r qty %d @ %d" % (o['id'], o['direction'], o['qty'], o['price'])
                already_order += o['qty']
        return already_order   

    def buy_condition(self, positionSoFar, tBestBid, tMA):
        """Tailored for each level.

        Will buy if the price is not above MA20 price. and current open order qtys + positionSoFar < self.order_limit for buy
        """        
        already_bought = self.find_ordered("buy")
        # basically we want 
        #  self.order_limit => positionSoFar +  already bought + to be ordered aka q_max
        q_max = self.order_limit - positionSoFar - already_bought  # this is the qty i can order without going over.
        print "\n\tIn BuyCond. tBestBid %r, ma %r max order %r - positionSoFar %r" \
              " - already_bought %r = q_max %r can buy?" % (tBestBid, tMA, self.order_limit, positionSoFar, already_bought, q_max),
        if (0 < tBestBid < tMA) and (q_max > self.threshold) and (already_bought + positionSoFar < self.order_limit):  # q_max > 50 because we still want reasonable bid quantity per each order
            print "..yes"
            return True
        print "..no"

    def sell_condition(self, positionSoFar, tBestAsk, tMA):
        """Tailored for each level.
            
        will sell if the price is not below MA20 price. and current open order + positionSoFar > -self.order_limit for sell
        """
        already_sold = self.find_ordered("sell") * -1
        # we want -self.order_limit >= positionSoFar + already_sold + To be ordered aka q_max
        q_max = abs(-1 * self.order_limit - positionSoFar - already_sold)
        print "\n\tIn SellCond. tBestAsk %r,ma %r max order %r - positionSoFar %r " \
              " - already_sold %r = q_max %r can sell?" % (tBestAsk, tMA, self.order_limit, positionSoFar, already_sold, q_max),
        if (tBestAsk > tMA) and (q_max > self.threshold) and (already_sold + positionSoFar > -1 * self.order_limit):
            print "..yes"
            return True
        print "..no"

    def run(self):
        ma_20_list = []         # moving average 20 lets the script know current trend.
        ma_20 = 0
        # global status_queue
        global gameOn
        nav = 0

        try:
            while nav < 250000 and self.sf.heartbeat():
                if abs(self.sf.get_position_so_far()) > 1000:
                    gameOn = False
                    break

                time.sleep(1.5)
                order_book = self.sf.get_order_book(self.stock)
                best_ask = self.sf.read_orderbook(order_book, "asks", "price", 1)
                best_bid = self.sf.read_orderbook(order_book, "bids", "price", 1)
                discount = .01
                if len(ma_20_list) > 20:  # Moving average 20 ticks
                    ma_20_list.pop(0)
                
                ma_20_list.append(self.sf.get_quote(self.stock).get("last"))
                ma_20 = sum(ma_20_list) / len(ma_20_list)
                             
                # cash, expectedPosition, nav, tempII = status_queue.get()

                position_so_far = self.sf.get_position_so_far()  # the sf.position_so_far is updated by the execution thread. much faster
                # print "\nB_Bid %d, B_Ask %d Last %d, average %d" % (best_bid, best_ask, ma_20_list[-1], ma_20),
                # print "temp %d" % (tempII)

                if self.buy_condition(position_so_far, best_bid, ma_20):
                    # loop through make multiple bids.
                    increment = int(best_bid * self.gap_percent * -1)
                    worst_bid = int(best_bid * (1 - self.worst_case))
                    already_bought = self.find_ordered("buy")  # this is the max amount i can bid without game over.
                    q_max = self.order_limit - position_so_far - already_bought
                    q_actual = int(abs(q_max * .5))
                    order_type = "limit"
                    actual_bid = best_bid

                    for actual_bid in range(best_bid, worst_bid, increment):
                        buy_order = self.sf.make_order(int(actual_bid * (1 + discount)), q_actual, self.stock, "buy", order_type)                        
                        print "\tPlaced BUY ord. id:%r +%r units @ %r %r time ordered %r" % (buy_order.get('id'), q_actual, 
                                                                                             buy_order.get('price'), order_type,
                                                                                             buy_order.get('ts')[buy_order.get('ts').index('T'):])
                        q_actual = int(abs(q_max * .25))
                        # order_type = "immediate-or-cancel"
                
                position_so_far = self.sf.get_position_so_far()   # check again because it might have been outdated.

                if self.sell_condition(position_so_far, best_ask, ma_20):
                    # loop through make multiple asks.
                    increment = int(best_ask * self.gap_percent)
                    worst_ask = int(best_ask * (1 + self.worst_case))
                    already_sold = self.find_ordered("sell") * -1  
                    # we want -self.order_limit >= position_so_far + already_sold + To be ordered aka q_max
                    q_max = abs(-1 * self.order_limit - position_so_far - already_sold)
                    q_actual = int(q_max * .5)
                    order_type = "limit"
                    actual_ask = best_ask
                    for actual_ask in range(best_ask, worst_ask, increment):
                        # print "actual ask %r and q_actual %r" %(actual_ask, q_actual)
                        sell_order = self.sf.make_order(int(actual_ask * (1 - discount)), q_actual, self.stock, "sell", order_type)                        
                        print "\tPlaced SELL ord. id:%r -%r units @ %r %r time ordered %r" % (sell_order.get('id'), q_actual, 
                                                                                              sell_order.get('price'), order_type,
                                                                                              sell_order.get('ts')[sell_order.get('ts').index('T'):])
                        q_actual = int(q_max * .25)
                        # order_type = "immediate-or-cancel"

            print "BuySell Closed, final values Nav. %d Positions. %d" % (nav, position_so_far)            
            gameOn = False
        except KeyboardInterrupt:
            print "ctrl+c pressed! leaving buy sell"
            gameOn = False


class CheckFill:
    """Decide if orders in my book should be cancelled or not."""

    def __init__(self, stockfighter):
        print "Initializing CheckFill.."
        self.sf = stockfighter
        self.stock = self.sf.tickers
        self.timeToWait = 3     # for how long the unfill orders can last.
        self.bid_diff_minimum = -.03
        self.bid_diff_maximum = .10
        self.ask_diff_minimum = -.10
        self.ask_diff_maximum = .03

    def identify_unfilled_orders(self, orderList, callback):
        """check through orderIDlist, run them against callback should_cancel_unfilled, then cancel the order if true."""
        for k, x in list(orderList.items()):  # list creates a snap shot of the dictionary so that we can proceed.
            if x["open"]:
                # print "\n%r" %(x)
                if callback(x):
                    print "\n\tCancelling %s id:%r units %d @ %d" % (x["direction"], x["id"], x["qty"], x["price"])
                    self.sf.delete_order(self.stock, x["id"])

    def should_cancel_unfilled(self, order):
        """Check if a given order should be cancelled.

        the main checking conditions are:
            whether the order price is out of money. ie. placed too high or too low the best price range.
            whether if this order is cancelled. will it drive the account out of the allowable condition. -1000 and 1000 units.
        """
        order_book = self.sf.get_order_book(self.stock)
        best_ask = self.sf.read_orderbook(order_book, "asks", "price", 1)
        best_bid = self.sf.read_orderbook(order_book, "bids", "price", 1)
        price = order["price"]
       
        if best_ask == 0:
            best_ask = price
        if best_bid == 0:
            best_bid = price
       
        if order["direction"] == "buy":
            diff = (best_bid - price) / float(price)
     
            print "\nJudging Buy order %d, best_bid %d, Price %d,  diff is %r, position_so_far %d, and order qty is %d" % (order['id'], best_bid, price, 
                                                                                                                            diff, self.sf.get_position_so_far(), order['qty'])
                      
            if (diff < self.bid_diff_minimum or diff > self.bid_diff_maximum):
                return True
  
        else:
            diff = (best_ask - price) / float(price)
            
            print "\nJudging Sell order%d, best_ask %r, Price %r,diff is %r, position_so_far %d, and order qty is %d" % (order['id'], best_ask, price, 
                                                                                                                          diff, self.sf.get_position_so_far(), order['qty'])
            
            if (diff > self.ask_diff_maximum or diff < self.ask_diff_minimum):
                return True
        return False

    def run(self):
        global gameOn
        try:
            while gameOn:
                time.sleep(2)
                # orders = self.sf.status_for_all_orders_in_stock(self.stock)
                orders = sf.orders
                self.identify_unfilled_orders(orders, self.should_cancel_unfilled)
        except KeyboardInterrupt:
            print "ctrl+c pressed! leaving checking fills"

if __name__ == '__main__':
    
    sf = gamemaster.StockFighter("dueling_bulldozers")
    # sf = gamemaster.StockFighter("sell_side")
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
            time.sleep(3)
    except KeyboardInterrupt:
        print "ctrl+c pressed! leaving FourthTradeMT"
    finally:
        printGraph = raw_input("Would you like to chart this level? y/n ")
        if printGraph.upper() == 'Y':
            sf.make_graphs()
