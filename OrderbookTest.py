import time
import gamemaster

print "Trying TestEX mode",
sf = gamemaster.StockFighter.test_mode()
time.sleep(3)
print "Initially..."
oBook = sf.get_order_book(sf.tickers)
print oBook.json()

print "Clearing the book..."
order = sf.make_order(1, 9999, sf.tickers, "buy", "market")
order = sf.make_order(1, 9999, sf.tickers, "sell", "market")
time.sleep(3)

print "Now Check the order book status"
order = sf.make_order(1000, 100, sf.tickers, "sell", "limit")
order = sf.make_order(1000, 50, sf.tickers, "buy", "limit")
order = sf.make_order(1000, 10, sf.tickers, "buy", "market")
order = sf.make_order(900, 40, sf.tickers, "buy", "limit")
order = sf.make_order(950, 50, sf.tickers, "buy", "limit")

try:
    time.sleep(10)
    print "Latest Quote"
    print sf.get_quote(sf.tickers)
    print "\nTrying get orderbook...",
    oBook = sf.get_order_book(sf.tickers)
    print oBook.json()
    
    sf.make_graphs()

except Exception as e:
    pass

