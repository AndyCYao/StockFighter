import time
import gamemaster

"""
print "Trying TestEX mode",
sf = gamemaster.StockFighter.test_mode()
"""
print "Try actual level"
sf = gamemaster.StockFighter("first_steps")


print "\n\nTesting Execution quote socket."
sf.execution_venue_ticker(sf.execution_socket)
time.sleep(2)
print "\nTrying placing order...",
order = sf.make_order(20000, 10, sf.tickers, "buy", "limit")
print "new order is %r" % (order)
# print "\nOk.. now delete the order",
# order = sf.delete_order(sf.tickers, order["id"])

"""
print "\nTrying get orderbook...",
oBook = sf.get_order_book(sf.tickers)
print oBook.json()

print "\nUsing the read_orderbook to find the best price...",
print sf.read_orderbook(oBook, "bids", "price", 1),
print sf.read_orderbook(oBook, "asks", "price", 1)

print "\nGet last quote...",
print sf.get_quote(sf.tickers)

print "\nSee all the open orders...",
orderList = sf.status_for_all_orders_in_stock(sf.tickers)
print orderList.json()

print "\nLoop through the list and check current current positions, cash, and expected positions..."
print sf.update_open_orders(orderList)
"""

print "Waiting for ctrl+c..."
while 1:
    time.sleep(5)

# print "Try actual level"
# sf = gamemaster.StockFighter("dueling_bulldozers")
