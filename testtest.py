import gamemaster
import time
import datetime
import Queue  # Queue encapsulates ideas of wait() , notify() , acquire() for multithread use

class BuySell:
    
    def __init__(self, stockfighter):
        print "Initializing BuySell..."
        self.sf = stockfighter
        self.start = time.time()
        self.sf.quote_venue_ticker(self.run)

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
    """  
    def read_quote(self, m):

        if m is None:
            self.sf.quote_venue_ticker(read_quote)
            return
        return "at readquote" + str(m) 
        # return m
    """
    def run(self, m):
        ma_20_list = []         # moving average 20 lets the script know current trend.
        ma_20 = 0
        gapPercent = .01        # how much different in % each order will be
        worstCase = .03         # how much different the best offer and worst offer will be
        stock = self.sf.tickers
        # global status_queue
        # global gameOn
        positionSoFar = 0
        nav = 0
        quoteTime = m['quoteTime']
        print quoteTime

        bidSize = m["bidSize"]
        askSize = m["askSize"]
        if bidSize > 0:
            bestBid = m["bid"]
        else:
            bestBid = 0
        if askSize >0:
            bestAsk = m["ask"]
        else:
            bestAsk = 0
        last = m["last"]
        TradeSize = m["lastSize"]
        TradeTime = m["lastTrade"]




        """        
            try:
                while nav < 250000:
                    if abs(positionSoFar) > 1000:
                        gameOn = False
                        break


                    oBook = self.sf.get_order_book(stock)
                    # will multiply base on the below info with gapPercent
                    bestAsk = self.sf.read_orderbook(oBook, "asks", "price", 1)
                    bestBid = self.sf.read_orderbook(oBook, "bids", "price", 1)
                    q_bid = min(self.sf.read_orderbook(oBook, "bids", "qty", 1), 30)
                    q_ask = min(self.sf.read_orderbook(oBook, "asks", "qty", 1), 30)
                    
                    
                    if len(ma_20_list) > 20:  # Moving average 20 ticks
                        ma_20_list.pop(0)
                    
                    ma_20_list.append(self.sf.get_quote(stock).get("last"))
                    ma_20 = sum(ma_20_list) / len(ma_20_list)
                                 
                    # positionSoFar, cash, expectedPosition, nav, tempII = status_queue.get()
                    # print "B_Bid %d, B_Ask %d Last %d, average %d" % (bestBid, bestAsk, ma_20_list[-1], ma_20)

                   
                    buyOrder = sf.make_order(actualBid, q_actual, stock, "buy", "limit")
                    print "\n\tBBBBB placed buy ord. +%d units at %d ID %d" % (q_bid, buyOrder.get('price'),
                                                                                buyOrder.get('id'))
                    sellOrder = sf.make_order(actualAsk, q_actual, stock, "sell", "limit")
                    print "\n\tSSSSS placed sell ord. -%d units at %d ID %d" % (q_ask, sellOrder.get('price'),
                                                                                        sellOrder.get('id'))
                    
                # print "BuySell Closed, final values Nav - %d Positions - %d" % (nav, positionSoFar)
        except KeyboardInterrupt:
            print "ctrl+c pressed! leaving buy sell"
            gameOn = False
        """
if __name__ == '__main__':
    
    sf = gamemaster.StockFighter("dueling_bulldozers")
    bs = BuySell(sf)
    
    # buy sell will now have its multithread initialize by the ws4py client thread.
    # bsThread = threading.Thread(target=bs.run, args=())
    # bs.run()
    try:
        while 1:
            time.sleep(4)               # the market bots sleep for 4 sec and make a trade
    except KeyboardInterrupt:
        print "ctrl+c pressed! leaving FourthTradeMT"
