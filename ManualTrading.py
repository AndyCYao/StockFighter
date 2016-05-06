"""The point of this script is to play around with the web order controls.

This script will loop and print the orderbook out 
but i will be inputting diff type of orders in the UI to see how the order book is reacting.
"""

import gamemaster
import time
import json

sf = gamemaster.StockFighter("irrational_exuberance")
# sf = gamemaster.StockFighter("dueling_bulldozers")
# sf = gamemaster.StockFighter("sell_side")
stock = sf.tickers
start = time.time()
end = time.time()
prevQuote = None
bid_stream = []
ask_stream = []

while end - start < 200:                
    time.sleep(1.5)
    o_book = sf.get_order_book(stock)
    print json.dumps(o_book.json(), indent=3)
    
    end = time.time()
sf.make_graphs()
    