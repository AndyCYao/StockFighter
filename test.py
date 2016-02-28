import gamemaster
import json

"""
y = gamemaster.StockFighter("sell_side")
r = y.status_for_all_orders_in_stock(y.tickers)
print r.json()

info = open("testJSON.json", "r")
currentInfo = json.load(info)

for x in currentInfo:
	print x

"""

sf = gamemaster.StockFighter("sell_side")
stock = sf.tickers

# make some orders
buyOrder = sf.make_order(90, 100, stock, "buy", "limit")
sellOrder = sf.make_order(100, 100, stock, "sell", "limit")

# try to loop through to see those orders.
orders = sf.status_for_all_orders_in_stock(stock)
sf.update_open_orders(orders.json())