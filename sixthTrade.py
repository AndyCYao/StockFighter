"""Sixth Trade - making_amends.

* I can use the execution socket to determine the standing ID and incomingID of a given trade.
* once i find out the list of accounts, i can create web sockets that can print out their trade activity.
* modified so that as soon as i found a new account i will immediatly create the websocket to track their order.
"""

from gamemaster import StockFighter as sF
import time


class SixthTradeSF(sF):
    """Implement my own socket for checking ids."""

    def __init__(self, level):
        sF.__init__(self, level)        
        sF.execution_venue_ticker(self, self.account, self.venues, self.tickers, self.discover_traders)
        self.players_in_venue = []
        self.orders = {}  # these are all the orders recorded in the orders accounts.
        self.last_id = 1

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

    def find_account(self, counter_party_id):
        """"""
        # Cancelling an order that's not mine produces an error message that indicates the account name.
        order_detail = self.delete_order(self.tickers, counter_party_id)
        # print json.dumps(order_detail, indent=3)
        try:
            if (counter_party_id != self.account):
                read_error = order_detail['error'].split()
                return read_error[-1].replace(".", "")
        except KeyError:
            print "error in find_account"
            print order_detail

    def discover_traders(self, m):
        """Use the execution socket to find who is the counterparty.
        New Version:
        get the order id of this order, find your previous order id.  then loop from previous to current 

        Previous version
        receive the counter_party_id from the execution socket, then attempt to cancel it. the error
        message for some reason says you're not the owner of x account. that's our counterparty account.
        """
        if m is not None:
            # print json.dumps(m, indent=4) 
            order_id = m['order']['id']            
            print "\n\tChecking accounts..",
            for missing_id in range(self.last_id, order_id):
                account = self.find_account(missing_id)
                if account not in self.players_in_venue:
                    print "Found %r" % (account),
                    self.players_in_venue.append(account)
                    self.execution_venue_ticker(account, trader.venues, trader.tickers, trader.add_to_orders)
            self.last_id = order_id

trader = SixthTradeSF("making_amends")
start = time.time()
end = time.time()

while end - start < 300:  #  find all the traders in the market.               
    trader.make_order(0, 1, trader.tickers, "buy", "market")
    time.sleep(3)
    print "found %r accounts" % (len(trader.players_in_venue))
    end = time.time()

while end - start < 1000:
    time.sleep(1)
    end = time.time()
    print ".",
print "Leaving sixthTrade, printing all the orders collected."
trader.analyze_orders()
trader.make_graphs()
