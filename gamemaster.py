"""Contains GameMaster and Stockfighter."""
import requests
import json
from ws4py.client.threadedclient import WebSocketClient
# import Queue


class GameMaster:
    """Contains the codes necessary to start the instance."""

    base_url = "https://api.stockfighter.io/ob/api"
    gm_url = "https://www.stockfighter.io/gm"

    def __init__(self):
        """to be worked on."""
        pass

    def get_is_instance_active(self, instanceID):
        """Return the state of instance."""
        header = {'X-Starfighter-Authorization': self.get_api_key()}
        full_url = "%s/instances/%s" % (self.gm_url, instanceID)
        response = requests.get(full_url, headers=header)
        # print json.dumps(response.json(), indent=4)
        is_true = response.json().get("state")
        return is_true
            
    def restart_level(self, instanceID):
        """Restart but keep the same info."""
        header = {'X-Starfighter-Authorization': self.get_api_key()}
        full_url = "%s/instances/%s/restart" % (self.gm_url, instanceID)
        response = requests.post(full_url, headers=header)
        # print response.json()
        return response

    def get_api_key(self):
        file = open('apikey.txt', 'r')
        apikey = file.readlines()[0]
        return apikey

    def get_instance_id(self):
        """Return a list of instances, not working yet."""
        header = {'X-Starfighter-Authorization': self.get_api_key}
        full_url = "%s/levels" % (self.gm_url)
        response = requests.get(full_url, headers=header)

        try:
            return response.text
        except ValueError as e:
            return{'error': e, 'raw_content': response.content}

    def post_level(self, level):
        header = {'X-Starfighter-Authorization': self.get_api_key()}
        full_url = "%s/levels/%s" % (self.gm_url, level)
        response = requests.post(full_url, headers=header)
        try:
            # print json.dumps(response.json(), indent=4)
            return response
        except ValueError as e:
            return{'error': e, 'raw_content': response.content}


class StockFighter:
    """Contain the methods neccessary to make API calls."""

    def __init__(self, LevelName):
        gm = GameMaster()
        apikey = gm.get_api_key()
        
        self.quotes = []     # used to store the websocket quote data.
        self.orderbook = []  # used in the websocket quote method to store the orderbook
        if LevelName == "test":
            self.account = "EXB123456"
            self.instanceID = "NotSureID"
            self.venues = "TESTEX"
            self.tickers = "FOOBAR"
        else:
            response = gm.post_level(LevelName)
            # print response.json()
            if response.json().get("ok"):
                self.account = response.json().get("account")
                self.instanceID = response.json().get("instanceId")
                self.venues = ''.join(response.json().get("venues"))
                self.tickers = ''.join(response.json().get("tickers"))
            else:
                print """Oops, something went wrong while connecting to Stockfighter, please try again in a 
                few minutes"""
                raise ValueError

        print "venue is %s , account is %s, id %s, ticker %s" % (self.venues, self.account,
                                                                 self.instanceID, self.tickers)
        
        self.header = {'X-Starfighter-Authorization': apikey}
        self.base_url = "https://api.stockfighter.io/ob/api"
        # used for storing a list of active orders made during this session.
        self.orders = self.status_for_all_orders_in_stock(self.tickers)
        self._positionSoFar, self._cash, self._expectedPosition = self.update_open_orders(self.orders)
        print "Game started...Actual Pos. is %d, expectedPosition %d, Cash %d" % (self._positionSoFar,
                                                                                  self._expectedPosition,
                                                                                  self._cash)
        # self.position_so_far_queue = Queue.Queue(maxsize=0)
        # self.position_so_far_queue.put(self._positionSoFar)  # this will be the outward facing variable.
        print "\nConnecting to quote socket...",
        self.quote_venue_ticker(self.account, self.venues, self.tickers, self.quote_socket)
        print "\nConnecting to execution socket...",
        self.execution_venue_ticker(self.account, self.venues, self.tickers, self.execution_socket)

    @classmethod
    def test_mode(cls):
        """Enable test mode with preset variables.

        Factory design pattern and overload in python.
        """
        test = cls("test")
        return test

    def heartbeat(self):
        """Check if venue is still up."""
        full_url = "%s/venues/%s/heartbeat" % (self.base_url, self.venues)
        response = requests.get(full_url).json()
        # print response.json()
        if not response["ok"]:
            print "%s's on fire" % (self.venues)
        return response["ok"]

    def get_stocks_on_a_venue(self):
        """List the stocks available for trading on a venue."""
        full_url = "%s/venues/%s/stocks" % (self.base_url, self.venues)
        response = requests.get(full_url, headers=self.header)
        return response

    def get_position_so_far(self):
        # rst = self.position_so_far_queue.get()
        rst = self._positionSoFar
        return rst 

    def get_expected_position(self):
        return self._expectedPosition

    def get_order_book(self, s):
        """retrieve the order book."""
        full_url = "%s/venues/%s/stocks/%s" % (self.base_url, self.venues, s)
        response = requests.get(full_url, headers=self.header)
        self.orderbook.append(response.json())
        return response
 
    def read_orderbook(self, oBook, direction, type, rank):
        """Return the detail of a orderbook node given the parameters.

        The lowest ask and highest bid is 1, and ++ as price gets worse.
        """
        try:
            best_result = oBook.json().get(direction)[rank].get(type)
        except (RuntimeError, TypeError, NameError, IndexError):
            best_result = 0
        return best_result

    def get_status_for_existing_order(self, venue, stock, order_id):
        
        full_url = "%s/venues/%s/stocks/%s/orders/%s" % (self.base_url, venue, stock, order_id)
        response = requests.get(full_url, headers=self.header)
        return response.json()

    def status_for_all_orders_in_stock(self, s):
        """Retrieve all orders in a given account, loads into a dictionary object."""
        my_orders = {}
        full_url = "%s/venues/%s/accounts/%s/stocks/%s/orders" % (self.base_url, self.venues, self.account, s)
        response = requests.get(full_url, headers=self.header)
        my_orders_json = response.json()
 
        for x in my_orders_json["orders"]:
            my_orders[int(x["id"])] = x
        return my_orders
 
    def update_open_orders(self, orders):
        """Loop through my orders and return positionSoFar, cash, and expectedPosition."""
        position_so_far = 0
        cash = 0
        expected_positions = 0
        for y in orders:
            total_filled = 0
            total_cost = 0
            x = orders[y]            
            # print "\n%r" % (x)
            for fill in x['fills']:
                total_filled += fill['qty']
                total_cost += fill['qty'] * fill["price"]

            qty = x["qty"] + total_filled  # x['qty'] becomes 0 if the order is cancelled. so we just add that to how much is filled already
            direction = x["direction"]
            if direction == "sell":
                total_filled = total_filled * -1
                total_cost = total_cost * -1
                qty = qty * -1
            position_so_far += total_filled
            expected_positions += qty            
            cash += total_cost * (-.01)  # -.01 because we are getting the correct unit
        return position_so_far, cash, expected_positions

    def execution_socket(self, m):
        """provide the same data as update_open_orders.

        done in a websocket way and faster, updates the self._positionSoFar,
        self._cash As the websocket sends message, this method
        adds the delta into the module level variables self._cash and self._positionSoFar.
        """
        if m is not None:
            # testing updating the self.orders straight from here. especially to see whether i can
            # see the remaining of the order. 
            id = int(m['order']['id'])
            # print "Execution Socket"
            # print json.dumps(m, indent=4)

            self.orders[id] = m['order']
            filled = m["filled"]
            price = m["price"]
            direction = m["order"]["direction"]
            original_qty = m["order"]["originalQty"]
            total_filled = m["order"]["totalFilled"]
            if direction == "sell":
                filled = filled * -1    
            self._positionSoFar += filled
            # self.position_so_far_queue.put(self._positionSoFar) # disabled for now.
            # -.01 because we are getting the correct unit
            self._cash += filled * price * (-.01)
            last = self.get_quote(self.tickers).get("last")
            if last is None:
                last = 0
            nav = self._cash + self._positionSoFar * last * (.01)
            nav_currency = '${:,.2f}'.format(nav)   # look prettier in the output below
            filled_at = m['filledAt'][m['filledAt'].index('T'):]
            print "\tUPDATE id:%d,Units %d @ %d %d/%d filled\tCurrent pos is %d, " \
                  " cash $%d,nav %s Filled At %r" % (id, filled, price, total_filled, original_qty, self._positionSoFar,
                                                     self._cash, nav_currency, filled_at)
     
        else:
            if self.heartbeat():  # sometimes m is None because venue is dead, this checks it.
                print "...restarting websocket..."
                self.execution_venue_ticker(self.account, self.venues, self.tickers, self.execution_socket)

    def quote_socket(self, m):
        """Receive quotes from websocket, and put them in a data list of dictionary.

        when game ends, push everything into draw graph.(using the make_graphs method). note 
        the socket sends LOTS of messages, even for any server side change unseen in the market,
        such as cancelled orders or unfill FOK. so need to do a comparison check before appending
        to the self.quote
        """
        if m is not None:
            if len(self.quotes) > 1:  # just comparing two quotes without quoteTime
                this_m = {i: m[i] for i in m if i != 'quoteTime'}
                last_m = {i: self.quotes[-1][i] for i in self.quotes[-1] if i != 'quoteTime'}                
                if not this_m == last_m:                    
                    self.quotes.append(m)
                    # print "Quote Socket"
                    # print json.dumps(m, indent=4)
            else:
                self.quotes.append(m)

    def make_graphs(self):
        """using the dictionaries gathered in self.quotes to update the graphs."""
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
            # my_orders = self.status_for_all_orders_in_stock(self.tickers)
            json.dump(self.orders, orders, indent=2)       
        
        try:
            print "Printing postmordem info into graph..."
            import QuotesChart
            QuotesChart.make_quote_chart()
        except Exception as e:
            # raise e
            print "Oops found error while making graph, please try again\n%r" % (e)
        
    def make_order(self, p, q, s, direction, orderType):
        order = {
            "account": self.account,
            "venue": self.venues,
            "symbol": s,
            "price": p,
            "qty": q,
            "direction": direction,
            "orderType": orderType
        }
        full_url = "%s/venues/%s/stocks/%s/orders" % (self.base_url, self.venues, s)
        response = requests.post(full_url, headers=self.header, data=json.dumps(order))
        
        # if order is ok, then load it into self.orders dictionary
        response_order = response.json()
        self.orders[response_order['id']] = response_order
        return response_order

    def delete_order(self, s, o_id):
        full_url = "%s/venues/%s/stocks/%s/orders/%s/cancel" % (self.base_url, self.venues, s, o_id)
        response = requests.post(full_url, headers=self.header)
        response_order = response.json()
        try:
            self.orders[response_order['id']] = response_order
        except KeyError:
            # i trap KeyError because in some level i may try to cancel orders not stored in my list
            pass

        return response.json()

    def get_quote(self, s):
        # Get last quote.
        full_url = "%s/venues/%s/stocks/%s/quote" % (self.base_url, self.venues, s)
        response = requests.get(full_url, headers=self.header)
        return response.json()

    def quote_venue_ticker(self, _account, _venue, _stock, callback):
        def wrapper(msg):
            
            if msg is None:
                callback(None)
            else:
                callback(msg['quote'])

        url = 'wss://api.stockfighter.io/ob/api/ws/%s/venues/%s/tickertape/stocks/%s' % (_account, _venue, _stock)
        self.SFSocket(url, wrapper)

    def execution_venue_ticker(self, _account, _venue, _stock, callback):
        def wrapper(msg):
            
            if msg is None:
                callback(None)
            else:
                callback(msg)

        url = 'wss://api.stockfighter.io/ob/api/ws/%s/venues/%s/executions/stocks/%s' % (_account, _venue, _stock)
        self.SFSocket(url, wrapper)

    class SFSocket(WebSocketClient):
        """with template from github jchristma/Stockfighter."""

        def __init__(self, url, m_callback):
            WebSocketClient.__init__(self, url)
            self.callback = m_callback
            self.connect()

        def closed(self, code, reason=None):
            print "Closing down Websocket! (%s) %s", code, reason
            self.callback(None)

        def received_message(self, m):
            try:
                # print m
                if m.is_text:
                    msg = json.loads(m.data.decode("utf-8"))
                    # print msg
                    self.callback(msg)
            except ValueError as e:
                self.log.error("Caught Exception in socket message: %s" % e)
                pass
        
        def opened(self):
            print "Connected to websocket!"
