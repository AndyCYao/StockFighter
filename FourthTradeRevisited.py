import gamemaster
import time

sf = gamemaster.StockFighter("dueling_bulldozers")
stock = sf.tickers
start = time.time()
end = time.time()

while end - start < 50:                
    oBook = sf.get_order_book(stock)
    print "*****\n%r\n" % (oBook.json())
    time.sleep(2)  # slow things down a bit, because we are querying the same information.
    end = time.time()
sf.make_graphs()
    