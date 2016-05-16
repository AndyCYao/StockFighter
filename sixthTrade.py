"""Sixth Trade - making_amends.

* I can use the execution socket to determine the standing ID and incomingID of a given trade.
* once i find out the list of accounts, i can create web sockets that can print out their trade activity.
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
        self.orders = {}  # these are all the orders recorded in the analyze_fills accounts.

    def analyze_fills(self, m):
        """This is the websocket that checks the account's fill.
        """
        if m is not None:
            # print json.dumps(m, indent=4)
            self.orders[m['order']['id']] = m


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
# trader = SixthTradeSF("dueling_bulldozers")
start = time.time()
end = time.time()

while end - start < 25: # give it 60 sec to find all the traders in the market.               
    trader.make_order(0, 1, trader.tickers, "buy", "market")
    time.sleep(3)
    print trader.players_in_venue
    end = time.time()

'''
for player in trader.players_in_venue:
    trader.execution_venue_ticker(player, trader.venues, trader.tickers, trader.analyze_fills)
'''
trader.execution_venue_ticker(trader.players_in_venue[-1], trader.venues, trader.tickers, trader.analyze_fills)

while end - start < 100:
    time.sleep(1)
    end = time.time()
print "Leaving sixthTrade, printing all the orders collected."
for o in trader.orders:
    print o
# trader.make_graphs()
