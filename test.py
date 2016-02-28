import gamemaster

y = gamemaster.StockFighter("sell_side")
r = y.status_for_all_orders_in_stock(y.tickers)
print r.json()