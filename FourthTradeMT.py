
"""
testing Multi Thread.
FourthTrade will be separated by two thread
1st Thread. -> Buy / Sell
    i.)     buy and sell while NAV is less than $250000
    ii.)    wait a sec, check NAV status.
    iii.)   repeat.
2nd Thread -> Read through open order and cancel unfilled
    i.)     check the order list for open orders.

due to the internal waits in the Queue library for get and put. we dont need to compensate with
our own time.wait in our own script.
"""
import threading
import gamemaster
import time
import datetime
import Queue  # Queue encapsulates ideas of wait() , notify() , acquire() for multithread use
import json

status_queue = Queue.Queue(maxsize=0)  # maxsize = 0 -> queue size is infinite.
gameOn = True
quote_queue = Queue.Queue(maxsize=0)  # used in the post-mordem.


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
        tempI = 0
        global status_queue
        global gameOn
        while gameOn:
            time.sleep(3)    # slow things down a bit, because we are querying the same information.
            orders = self.sf.status_for_all_orders_in_stock(stock)
            positionSoFar, cash, expectedPosition = self.sf.update_open_orders(orders)

            nav = cash + positionSoFar * self.sf.get_quote(stock).get("last") * (.01)
            status_queue.put([cash, expectedPosition, nav, tempI])
            nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below
            print "----\nT%d approximate Pos. %d, Expected Pos. %d, NAV %s" % \
                  ((time.time() - self.start), positionSoFar, expectedPosition, nav_currency),
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
        if tBestBid != 0:
            if tExpectedPosition <= 0 and positionSoFar < 500 and tBestBid < tMA:
                return True
        return False

    def sell_condition(self, tExpectedPosition, positionSoFar, tBestAsk, tMA):
        """to be tailored for each level.
            will sell if the price is not below MA20 price.
        """
        if tBestAsk != 0:
            if tExpectedPosition >= 0 and positionSoFar > -500 and tBestAsk > tMA:
                return True

    def fluff_orders(self, positionSoFar, tBestAsk, tBestBid, stock):
        """ if have extreme position in long or short, i will make fill or kill orders to make my orders attractive.
        ex. if long 500, i will make high bid orders and vice versa. 
        """
       
        if positionSoFar < -500:
            Order = sf.make_order(int(tBestAsk * 1.3), 700, stock, "sell", "fill-or-kill")
        elif positionSoFar < 500:
            return
        elif positionSoFar < 1000:
            Order = sf.make_order(int(tBestBid * .7), 700, stock, "buy", "fill-or-kill")
        
        print "\n\tFLUFF placed %s ord. %d units at %d ID %d" % (Order.get('direction'), 1000, Order.get('price'),
                                                                 Order.get('id'))
      
    def run(self):
        ma_20_list = []         # moving average 20 lets the script know current trend.
        ma_20 = 0
        gapPercent = .01        # how much different in % each order will be
        worstCase = .03         # how much different the best offer and worst offer will be
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
                # quoteTime = oBook.json()['ts']

                if len(ma_20_list) > 20:  # Moving average 20 ticks
                    ma_20_list.pop(0)
                
                ma_20_list.append(self.sf.get_quote(stock).get("last"))
                ma_20 = sum(ma_20_list) / len(ma_20_list)
                             
                cash, expectedPosition, nav, tempII = status_queue.get()
                positionSoFar = sf.positionSoFar  # the sf.positionSoFar is updated by the execution thread. much faster
                print "\nB_Bid %d, B_Ask %d Last %d, average %d" % (bestBid, bestAsk, ma_20_list[-1], ma_20),
                # print "temp %d" % (tempII)

                if self.buy_condition(expectedPosition, positionSoFar, bestBid, ma_20):
                    # loop through the gapPercent and make multiple bids.
                    increment = int(bestBid * gapPercent * -1)
                    worstBid = int(bestBid * (1 - worstCase))
                    q_increment = int(q_bid * gapPercent)
                    q_actual = q_bid
                    for actualBid in range(bestBid, worstBid, increment):
                        buyOrder = sf.make_order(actualBid, q_actual, stock, "buy", "limit")                        
                        print "\n\tBBBBB placed buy ord. +%d units at %d ID %d" % (q_bid, buyOrder.get('price'),
                                                                                   buyOrder.get('id'))
                        
                        q_actual -= q_increment

                if self.sell_condition(expectedPosition, positionSoFar, bestAsk, ma_20):
                    # loop through the gapPercent and make multiple asks.
                    increment = int(bestAsk * gapPercent)
                    worstAsk = int(bestAsk * (1 + worstCase))
                    q_increment = int(q_ask * gapPercent)
                    q_actual = q_ask
                    for actualAsk in range(bestAsk, worstAsk, increment):
                        sellOrder = sf.make_order(actualAsk, q_actual, stock, "sell", "limit")                        
                        print "\n\tSSSSS placed sell ord. -%d units at %d ID %d" % (q_ask, sellOrder.get('price'),
                                                                                    sellOrder.get('id'))
                        
                        q_actual -= q_increment

                # self.fluff_orders(positionSoFar, bestAsk, bestBid, stock)

            print "BuySell Closed, final values Nav - %d Positions - %d" % (nav, positionSoFar)
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
        """if this order is out of money, then cancel it"""
        oBook = self.sf.get_order_book(self.stock)
        s_BestAsk = self.sf.read_orderbook(oBook, "asks", "price", 1)
        s_BestBid = self.sf.read_orderbook(oBook, "bids", "price", 1)
        price = order["price"]

        # this is in ISO 8601 time. stripping the microseconds we are not that concern
        ts = order["ts"].split(".")[0]
        o_time = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
        
        timeDiff = datetime.datetime.utcnow() - o_time
        
        if timeDiff < datetime.timedelta(seconds=self.timeToWait):
            if order["direction"] == "buy":
                diff = (s_BestBid - price) / price
                if diff < -.1:
                    return True
            else:
                diff = (s_BestAsk - price) / price
                if diff > .1:
                    return True
        else:
            return True
        return False

    def run(self):
        global gameOn
        try:
            while gameOn:
                time.sleep(3)
                orders = self.sf.status_for_all_orders_in_stock(self.stock)
                self.identify_unfilled_orders(orders, self.should_cancel_unfilled)
        except KeyboardInterrupt:
            print "ctrl+c pressed! leaving checking fills"


def QuoteSocket(m):
    """receives data, put into quote_queue for postmordem purpose. """
    quote_queue.put(m)

if __name__ == '__main__':
    
    sf = gamemaster.StockFighter("dueling_bulldozers")
    bs = BuySell(sf)
    cf = CheckFill(sf)
    cs = CurrentStatus(sf)
    sf.quote_venue_ticker(QuoteSocket)
    sf.execution_venue_ticker(sf.execution_socket)

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
        open("currentInfo.json", 'w').close()  # doing this clears everything first
        with open("currentInfo.json", "a") as settings:
            settings.write("[")
            while gameOn and sf.heartbeat():
                quotes = quote_queue.get()
                json.dump(quotes, settings)  # printing the order book for postmordem.
                settings.write(",")

    except KeyboardInterrupt:
        print "ctrl+c pressed! leaving FourthTradeMT"

    settings.seek(-1, 2) # -1 is looking at the last item from the end, in this case comma. 
    settings.truncate()  # removes the character that above line found.
    settings.write("]")
    settings.close()
    print "Printing postmordem info into graph..."
    import CurrentInfoChart
    CurrentInfoChart.main()
