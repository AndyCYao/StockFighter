import gamemaster
import time

# sf = gamemaster.StockFighter("dueling_bulldozers")
sf = gamemaster.StockFighter("sell_side")
stock = sf.tickers
start = time.time()
end = time.time()

while end - start < 50:                
    
    try:
        quote = sf.quotes[-1]
    except:
        quote = 0
    oBook = sf.get_order_book(stock)
    print "printing\n %r \n and \n %r\n" % (oBook.json(), quote)

    # s_BestAsk = sf.read_orderbook(oBook, "asks", "price", 1)
    # s_BestBid = sf.read_orderbook(oBook, "bids", "price", 1)
    # q_BestAsk = sf.quotes[-1]["ask"]
    # q_BestBid = sf.quotes[-1]["bid"]
    # print "*****\nOrderBook Bid , quotes BestBid\n" % (s_BestBid, q_BestBid)
    # print "*****\nOrderBook Ask , quotes BestAsk\n" % (s_BestAsk, q_BestAsk)
    time.sleep(2)  # slow things down a bit, because we are querying the same information.
    end = time.time()
sf.make_graphs()
    