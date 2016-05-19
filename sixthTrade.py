"""Sixth Trade - making_amends.

* I can use the execution socket to determine the standing ID and incomingID of a given trade.
* once i find out the list of accounts, i can create web sockets that can print out their trade activity.
* then we can identify unusual trade prices and volumn movement. (Read on about SONAR system)
read about naive bayes, logistics regressions to identify suspicious accounts. 
"""

from gamemaster import StockFighter as sF
import time
import json


class SixthTradeSF(sF):
    """Implement my own socket for checking ids."""

    def __init__(self, level):
        sF.__init__(self, level)        
        sF.execution_venue_ticker(self, self.account, self.venues, self.tickers, self.discover_traders)
        self.players_in_venue = []
        self.orders = {}  # these are all the orders recorded in the orders accounts.

    def add_to_orders(self, m):
        """Websocket that checks the account's fill."""
        if m is not None:
            self.orders[m['order']['id']] = m['order']

    def analyze_orders(self):
        """Print on browser the relevant info.

        Read through the self.orders
        including - Cash, Nav, count of orders.
        """
        last = self.quotes[-1]["last"]
        if last is None:
            last = 0

        for player in self.players_in_venue:
            player_orders = {k: v for k, v in self.orders.items() if v['account'] == player}
            positionSoFar, cash, expectedPos = self.update_open_orders(player_orders)
            nav = cash + positionSoFar * last * (.01)
            print "\nAccount: %r\nPosition: %r\nCash: %r\nNAV: %r\nNumber of orders: %r" % (player, positionSoFar, 
                                                                                            cash, nav, len(player_orders))

    def load_data_into_json(self):
        """Load the data into json files. similar to make_graphs in the gamemaster."""
        with open("ResultQuoteSocket.json", "r+b") as settings:
            settings.seek(0)  # The seek and truncate line wipes out everythin in the settings file.
            settings.truncate()
            json.dump(self.quotes, settings, indent=2)        
        with open("resultOrderBook.json", "r+b") as orderBook:
            orderBook.seek(0)  # The seek and truncate line wipes out everythin in the orderBook file.
            orderBook.truncate()
            json.dump(self.orderbook, orderBook, indent=2)        
        with open("resultOrders.json", "r+b") as orders:
            orders.seek(0)  # The seek and truncate line wipes out everythin in the orders file.
            orders.truncate()
            json.dump(self.orders, orders, indent=2)       

    def discover_traders(self, m):
        """Use the execution socket to find who is the counterparty.

        receive the counter_party_id from the execution socket, then attempt to cancel it. the error
        message for some reason says you're not the owner of x account. that's our counterparty account.
        """
        if m is not None:
            # print json.dumps(m, indent=4) 
            standing_id = m['standingId']
            incoming_id = m['incomingId']
            order_id = m['order']['id']
            
            if standing_id == order_id:
                counter_party_id = incoming_id
            else:
                counter_party_id = standing_id
            # Cancelling an order that's not mine produces an error message that indicates the account name.
            order_detail = self.delete_order(self.tickers, counter_party_id)
            # print json.dumps(order_detail, indent=3)
            read_error = order_detail['error'].split()
            account = read_error[-1].replace(".", "")
            if account not in self.players_in_venue:
                print "\n\tFound new bot %r" % (account)
                self.players_in_venue.append(account)
            

trader = SixthTradeSF("making_amends")
start = time.time()
end = time.time()

while end - start < 60:  # give it 60 sec to find all the traders in the market.               
    trader.make_order(0, 1, trader.tickers, "buy", "market")
    time.sleep(3)
    print trader.players_in_venue
    end = time.time()

for player in trader.players_in_venue:
    trader.execution_venue_ticker(player, trader.venues, trader.tickers, trader.add_to_orders)

# trader.execution_venue_ticker(trader.players_in_venue[-1], trader.venues, trader.tickers, trader.add_to_orders)

while end - start < 2000:
    time.sleep(1)
    end = time.time()
    print ".",
print "Leaving sixthTrade, printing all the orders collected."
trader.analyze_orders()
trader.load_data_into_json()
