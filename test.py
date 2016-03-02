
import gamemaster
import json
#  import time
from ws4py.client.threadedclient import WebSocketClient


class SFSocket(WebSocketClient):
    
    def closed(self, code, reason=None):
        print "Closing down! (%s) %s", code, reason

    def received_message(self, m):
        try:
            if m.is_text:
                msg = json.loads(m.data.decode("utf-8"))
                print msg
        except ValueError as e:
            self.log.error("Caught Exception in socket message: %s" % e)
            pass

if __name__ == '__main__':
    try:
        sf = gamemaster.StockFighter("sell_side")
        stock = sf.tickers
        account = sf.account
        venues = sf.venues

        uri = 'wss://api.stockfighter.io/ob/api/ws/%s/venues/%s/tickertape' % (account, venues)
        ws = SFSocket(uri, protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()





"""
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