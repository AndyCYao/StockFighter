"""Sixth Trade - making_amends.

* I can use the execution socket to determine the standing ID and incomingID of a given trade.
* I determine which id is my trade. and run the other ID in status_for_an_existing_order. which can tell me the account number.
    problem. the get_status_for_existing_order doesn't allow me to view the detail of an order that's not mine. 
* when i try to cancel the order of a counter_party, the error message says you have to own account x. 
* once i know the trading accounts, i can just use that account into the websocket to check their status of order.
"""

from gamemaster import StockFighter as sF
import time
# import json


class SixthTradeSF(sF):
    """Implement my own socket for checking ids."""

    def __init__(self, level):
        sF.__init__(self, level)        
        sF.execution_venue_ticker(self, self.discover_traders)
        self.players_in_venue = []

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

while end - start < 60:                
    trader.make_order(0, 1, trader.tickers, "buy", "market")
    time.sleep(3)
    print trader.players_in_venue
    
    end = time.time()
trader.make_graphs()
