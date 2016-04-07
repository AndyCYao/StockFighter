import time
import gamemaster

print "Trying TestEX mode",
sf = gamemaster.StockFighter.test_mode()

"""
print "Try actual level"
sf = gamemaster.StockFighter("dueling_bulldozers")
"""

print "\nTrying placing order...",
order = sf.make_order(100, 100, sf.tickers, "buy", "limit")
order = sf.make_order(200, 200, sf.tickers, "buy", "limit")
print order

time.sleep(2)

print "\nOk.. now delete the order",
print sf.delete_order(sf.tickers, order["id"])

print "\nTrying get orderbook...",
oBook = sf.get_order_book(sf.tickers)
print str(oBook.json())[0:80]

print "\nUsing the read_orderbook to find the best price...",
print sf.read_orderbook(oBook, "bids", "price", 1),
print sf.read_orderbook(oBook, "asks", "price", 1)

print "\nGet last quote...",
print sf.get_quote(sf.tickers)

print "\nSee all the open orders...",
orderList = sf.status_for_all_orders_in_stock(sf.tickers)
print str(orderList)[0:80]

print "\nLoop through the list and check current current positions, cash, and expected positions..."
print sf.update_open_orders(orderList)
print "Ok.. printing graphs."
sf.make_graphs()
print "Waiting for ctrl+c..."
try:
    while 1:
        time.sleep(1)
except KeyboardInterrupt:
    pass
except Exception as e:
    pass
# print "Try actual level"
# sf = gamemaster.StockFighter("dueling_bulldozers")
