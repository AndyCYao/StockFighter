
import gamemaster
import json
#  import time
# from ws4py.client.threadedclient import WebSocketClient
import datetime

# x = "2016-03-11T06:16:41.85000Z"
a = "2016-03-11T06:25:27.179683641Z"
b = a.split(".")[0]
# print b
o_time = datetime.datetime.strptime(b, '%Y-%m-%dT%H:%M:%S')

print o_time
print datetime.datetime.utcnow()
# print datetime.datetime.now()

print (datetime.datetime.utcnow() - o_time) < datetime.timedelta(seconds=30)
"""
sf = gamemaster.StockFighter("dueling_bulldozers")
stock = sf.tickers
account = sf.account
venues = sf.venues
buyOrder = sf.make_order(90, 100, stock, "buy", "limit")
buyOrder = sf.make_order(90, 100, stock, "buy", "limit")
buyOrder = sf.make_order(90, 100, stock, "buy", "limit")

sellOrder = sf.make_order(100, 100, stock, "sell", "limit")


orderIDList = sf.status_for_all_orders_in_stock(stock)
x = orderIDList.json()
print x
for y in x:
    print y
    #if y["open"]:
        #print(y["id"])


def identify_unfilled_orders(orderList):
    check through orderIDlist, and return a list of 
    orders that is not gonna be filled at the moment because
    the price is out the money. 
    
    orderIDs = []

    for x in orderList["orders"]:
        if x["open"] and x["direction"] == "sell":
           orderIDs.append(x["id"]) 


    return orderIDs
    



if __name__ == '__main__':
    try:
        sf = gamemaster.StockFighter("sell_side")
        stock = sf.tickers
        account = sf.account
        venues = sf.venues

        def ReadQuote(m):
            print "printing whats received from ReadQuote %s" % (m)

        while True:
            sf.quote_venue_ticker(ReadQuote)

    except KeyboardInterrupt:
        print "Ctrl + C Pressed"
        

    y = gamemaster.StockFighter("sell_side")


    r = y.status_for_all_orders_in_stock(y.tickers)
    print r.json()

    info = open("testJSON.json", "r")
    currentInfo = json.load(info)

    for x in currentInfo:
        print x


    sf = gamemaster.StockFighter("sell_side")
    stock = sf.tickers

    # make some orders
    buyOrder = sf.make_order(90, 100, stock, "buy", "limit")
    sellOrder = sf.make_order(100, 100, stock, "sell", "limit")

    # sf.update_open_orders(orders.json())


    try:
        while True:
            time.sleep(1)
            print "waiting.."
    except KeyboardInterrupt:
        
        # try to loop through to see those orders.
        try:
            orders = sf.status_for_all_orders_in_stock(stock)
        except:
            print "error in making orders"

        print "Write to file!"
        EndLog = open("results.txt", "w")
        EndLog.write("test test andy")
        json.dump(orders, EndLog)
        EndLog.close()
        print "ctrl+c pressed!"



    x = 0
    while x < 20:
        
        # print x
        

        # print "Wait for keyboard interrupt"
        if x % 3 == 0 or x % 5 == 0:
            print "%d divided by 3 or 5" %(x)
        else:
            print "%d fizz" %(x)

        x += 1

"""