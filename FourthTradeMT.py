
"""

testing Multi Thread.
FourthTrade will be separated by two thread
1st Thread. -> Buy / Sell
    i.)     buy and sell while NAV is less than $250000
    ii.)    wait a sec, check NAV status.
    iii.)   repeat.
2nd Thread -> Read through open order and cancel unfilled
    i.)     check the order list for open orders.

"""
import threading
import gamemaster
import time
import datetime
import Queue

status_queue = Queue.Queue(maxsize=0)

class CurrentStatus:
    """is now separated from BuySell. runs and update
    positionSoFar, cash, expectedPosition, NAV.
    """
    
    def __init__(self, stockfighter):
        print "Initializing CurrentStatus..."
        self.sf = stockfighter
        self.start = time.time()

    def run(self):
        stock = self.sf.tickers
        tempI = 0
        while 1:
            time.sleep(1)    # slow things down a bit, because we are querying the same information.
            orderIDList = self.sf.status_for_all_orders_in_stock(stock)
            positionSoFar, cash, expectedPosition = self.sf.update_open_orders(orderIDList.json())

            nav = cash + positionSoFar * self.sf.get_quote(stock).get("last") * (.01)
            status_queue.put([positionSoFar, cash, expectedPosition, nav, tempI])
            nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below
            print "----\nT%d Pos. %d, Expected Pos. %d, NAV %s tempI %d " % \
                  ((time.time() - self.start), positionSoFar, expectedPosition, nav_currency, tempI)
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
        if tBestAsk is not None or tBestAsk != 0:
            if tExpectedPosition >= 0 and positionSoFar > -500 and tBestAsk > tMA:
                return True

    def run(self):
        
        ma_20_list = []         # moving average 20 lets the script know current trend.
        ma_20 = 0
        gapPercent = .01        # how much different in % each order will be
        worstCase = .03  # how much different the best offer and worst offer will be
        stock = self.sf.tickers
        
        positionSoFar, cash, expectedPosition, nav, tempII = status_queue.get()
        status_queue.task_done()
        nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below

        try:
            while nav < 250000:
                if abs(positionSoFar) > 1000:
                    break

                time.sleep(1)    # slow things down a bit, because we are querying the same information.
                oBook = self.sf.get_order_book(stock)

                # will multiply base on the below info with gapPercent
                bestAsk = self.sf.read_orderbook(oBook, "asks", "price")
                bestBid = self.sf.read_orderbook(oBook, "bids", "price")
                q_bid = min(self.sf.read_orderbook(oBook, "bids", "qty"), 50)
                q_ask = min(self.sf.read_orderbook(oBook, "asks", "qty"), 50)

                if len(ma_20_list) > 20:  # Moving average 20 ticks
                    ma_20_list.pop(0)
                
                ma_20_list.append(self.sf.get_quote(stock).get("last"))
                ma_20 = sum(ma_20_list) / len(ma_20_list)
                
                print "BS- Pos. %d, Expected Pos. %d, NAV %s tempI %d" % \
                    (positionSoFar, expectedPosition, nav_currency, tempII)
                print "B_Bid %d, B_Ask %d Last %d, average %d" % (bestBid, bestAsk, ma_20_list[-1], ma_20)

                if self.buy_condition(expectedPosition, positionSoFar, bestBid, ma_20):
                    # loop through the gapPercent and make multiple bids.
                    increment = int(bestBid * gapPercent * -1)
                    worstBid = int(bestBid * (1 - worstCase))
                    q_increment = int(q_bid * gapPercent)
                    q_actual = q_bid
                    for actualBid in range(bestBid, worstBid, increment):
                        # print actualBid, q_actual
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


            print "BuySell Closed, final values Nav - %d Positions - %d" % (nav, positionSoFar)
        except KeyboardInterrupt:
            print "ctrl+c pressed! leaving buy sell"


class CheckFill:
    
    def __init__(self, stockfighter):
        print "Initializing CheckFill.."
        self.sf = stockfighter
        self.stock = self.sf.tickers
        self.timeToWait = 5     # for how long the unfill orders can last.

    def identify_unfilled_orders(self, orderList, callback):
        """check through orderIDlist, and return a list of
        orders that is not gonna be filled at the moment because
        the price is out the money.
        """
        for x in orderList["orders"]:
            if x["open"]:
                if callback(x):
                    print "\n\tCancelling %s %s units at %s ID %s \n" % (x["direction"], x["qty"], x["price"], x["id"])
                    self.sf.delete_order(self.stock, x["id"])

    def should_cancel_unfilled(self, order):
        """if this order is out of money, then cancel it"""
        oBook = self.sf.get_order_book(self.stock)
        s_BestAsk = self.sf.read_orderbook(oBook, "asks", "price")
        s_BestBid = self.sf.read_orderbook(oBook, "bids", "price")
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
        try:
            while 1:
                time.sleep(2)
                orderIDList = self.sf.status_for_all_orders_in_stock(self.stock)
                self.identify_unfilled_orders(orderIDList.json(), self.should_cancel_unfilled)
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
    bsThread.daemon = True  # this allows the thread to exit once the main thread exits.
    cfThread.daemon = True
    csThread.daemon = True
    bsThread.start()
    cfThread.start()
    csThread.start()
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print "ctrl+c pressed! leaving FourthTradeMT"