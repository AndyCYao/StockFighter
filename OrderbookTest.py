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

print "Now Check the order book status"
order = sf.make_order(1000, 100, sf.tickers, "sell", "limit")
time.sleep(3)
order = sf.make_order(1000, 50, sf.tickers, "buy", "limit")
order = sf.make_order(1000, 10, sf.tickers, "buy", "market")
try:
    print "\nTrying get orderbook...",
    oBook = sf.get_order_book(sf.tickers)
    print oBook.json()
    time.sleep(3)
    sf.make_graphs()

except Exception as e:
    pass

