"""Sixth Trade - making_amends.

*This script will run when after sixthTrade is finish. this will read through the resultOrders generated, and 
find a list of ids not in that resultOrders, then it will attempt to cancel every order in hope to find the owner of that trade.
"""

from gamemaster import StockFighter as sF
import json


class SixthTradeSF(sF):
    """Implement my own socket for checking ids."""

    def __init__(self, level):
        sF.__init__(self, level)        
        with open('ResultOrders.json', 'r') as ordersJson:
            self.orders = json.load(ordersJson)
        self.players_in_venue = set([v['account'] for k, v in self.orders.items()])
        print 'initially found %r account ' % (len(self.players_in_venue))
        self.find_missing_id()

    def find_account(self, counter_party_id):
        """Cancelling an order that's not mine produces an error message that indicates the account name."""
        order_detail = self.delete_order(self.tickers, counter_party_id)
        read_error = order_detail['error'].split()
        return read_error[-1].replace(".", "")

    def find_missing_id(self):
        """"""
        missed_players = set()
        order_id = [int(x) for x in self.orders.keys()]
        order_id.sort()
        differences = list(set(range(order_id[0], order_id[-1] + 1)).difference(order_id))
        for missing_id in differences:
            account = self.find_account(missing_id)
            if account not in self.players_in_venue:
                missed_players.add(account)

        print "missed %r players" % (len(missed_players))
        print missed_players

trader = SixthTradeSF("making_amends")
