import time
import gamemaster
import json

"""
print "Trying TestEX mode",
sf = gamemaster.StockFighter.test_mode()

"""
print "Try actual level"
sf = gamemaster.StockFighter("dueling_bulldozers")

def ExecutionSocket(m):
    currentPos = 0
    currentPosCash = 0
    expectedPos = 0
    print "/n***** IN websocket ****"
    print m
    print "*****"
    """
    for x in m["order"]:
        totalFilled = x["totalFilled"]
        # originalQty = x["originalQty"]
        qty = x["qty"] + totalFilled
        direction = x["direction"]
        price = x["price"]
           
        if direction == "sell":
            totalFilled = totalFilled * -1
            qty = qty * -1
            currentPos += totalFilled
            expectedPos += qty
            # -.01 because we are getting the correct unit
            currentPosCash += totalFilled * price * (-.01)

        print "current pos is %d and $%d" %(currentPos, currentPosCash)
        return currentPos, currentPosCash, expectedPos
    """

print "\nTrying placing order...",
order = sf.make_order(100, 100, sf.tickers, "buy", "limit")
order = sf.make_order(200, 200, sf.tickers, "buy", "limit")
print order
print "\n\nTesting Execution quote socket."
time.sleep(2)
sf.execution_venue_ticker(ExecutionSocket)

print "\nOk.. now delete the order",
print sf.delete_order(sf.tickers, order["id"])

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

def read_quote(m):
    if m is None:
    	sf.quote_venue_ticker(read_quote)
    	return
    print '\t --- Quote from ticker: %s... ---\n' % str(m)[:40],

print "\n\nFinally, testing the quote web socket..."
sf.quote_venue_ticker(read_quote)



print "Waiting for ctrl+c..."
while 1:
	print ("main thread sleeping...")
	time.sleep(1)

# print "Try actual level"
# sf = gamemaster.StockFighter("dueling_bulldozers")
