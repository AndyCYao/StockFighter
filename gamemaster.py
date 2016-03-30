"""Contains GameMaster and Stockfighter."""
import requests
import json
from ws4py.client.threadedclient import WebSocketClient

class GameMaster:
    """Contains the codes necessary to start the instance."""

    base_url = "https://api.stockfighter.io/ob/api"
    gm_url = "https://www.stockfighter.io/gm"

    def __init__(self):
        """to be worked on."""
        pass

    def check_if_instance_is_active(self, instanceID):
        "returns the state of instance."
        is_true = False
        header = {'X-Starfighter-Authorization': self.get_api_key()}
        full_url = "%s/instances/%s" % (self.gm_url, instanceID)
        response = requests.get(full_url, headers=header)
        is_true = response.json().get("state")
        return is_true
            
    def restart_level(self, instanceID):
        """ restart but keep the same info."""
        header = {'X-Starfighter-Authorization': self.get_api_key()}
        full_url = "%s/instances/%s/restart" % (self.gm_url, instanceID)
        response = requests.post(full_url, headers=header)
        print "****In restart_level****"
        # print response.json()
        return response

    def get_api_key(self):
        file = open('apikey.txt', 'r')
        apikey = file.readlines()[0]
        return apikey

    def get_instance_id(self):
        """returns a list of instances, not working yet"""
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
            # print response.json()
            # self.write_to_setting(response.json())  # for retrieving later
            return response
        except ValueError as e:
            return{'error': e, 'raw_content': response.content}


class StockFighter:
    """Contains the methods neccessary to make API calls."""
    def __init__(self, LevelName):
        gm = GameMaster()
        apikey = gm.get_api_key()
        # look in the currentinfo, if exists check if its active
        # if active prompt user if they want to restart or new
      
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
                print "Oops, something went wrong, try again."
                raise ValueError

        print "venue is %s , account is %s, id %s, ticker %s" % (self.venues, self.account,
                                                                 self.instanceID, self.tickers)
        self.header = {'X-Starfighter-Authorization': apikey}
        self.base_url = "https://api.stockfighter.io/ob/api"

        self.orders = {}  # used for storing a list of active orders made during this session.
        orderIDList = self.status_for_all_orders_in_stock(self.tickers)
        self.positionSoFar, self.cash, self.expectedPosition = self.update_open_orders(orderIDList)
        print "Game restarted.. Actual Pos. is %d" % (self.positionSoFar)

    @classmethod
    def test_mode(cls):
        """learn about factory design pattern and overload in python."""
        test = cls("test")
        return test

    def heartbeat(self):
        """ check if venue is still up """
        full_url = "%s/venues/%s/heartbeat" % (self.base_url, self.venues)
        response = requests.get(full_url).json()
        # print response.json()
        if not response["ok"]:
            print "%s's on fire" % (self.venues)

        return response["ok"]

    def get_order_book(self, s):
        """retrieve the order book"""
        full_url = "%s/venues/%s/stocks/%s" % (self.base_url, self.venues, s)
        response = requests.get(full_url, headers=self.header)
        return response
 
    def read_orderbook(self, oBook, direction, type, rank):
        # this returns the best price of buy or sell, the
        # lowest ask and highest bid is 1, and ++ as price gets worse.
        try:
            best_result = oBook.json().get(direction)[rank].get(type)
        except (RuntimeError, TypeError, NameError, IndexError):
            best_result = 0
        return best_result

    def status_for_all_orders_in_stock(self, s):
        """ retrieve all orders given account """
        full_url = "%s/venues/%s/accounts/%s/stocks/%s/orders" % (self.base_url, self.venues, self.account, s)
        response = requests.get(full_url, headers=self.header)
        return response

    def update_open_orders(self, orderList):
        """loops through the open ids and check them see.
        how many have been filled. i am changing it to loop through the orders from.
        status_for_all_orders_in_stock
        """
        orderListJson = orderList.json()
        currentPos = 0
        currentPosCash = 0
        expectedPos = 0
        # print "******IN HTTP REST******"
        # print orderListJson
        for x in orderListJson["orders"]:
            totalFilled = x["totalFilled"]
            # originalQty = x["originalQty"]
            qty = x["qty"] + totalFilled
            direction = x["direction"]
            price = x["price"]
           
            if direction == "sell":
                totalFilled = totalFilled * -1
                # originalQty = originalQty * -1
                qty = qty * -1
            currentPos += totalFilled
            # expectedPos += originalQty
            expectedPos += qty
            # -.01 because we are getting the correct unit
            currentPosCash += totalFilled * price * (-.01)

        # print "current pos is %d and $%d" %(currentPos, currentPosCash)
        return currentPos, currentPosCash, expectedPos


    def execution_socket(self, m):
        """provides the same data as from status_for_all_orders_in_stock, just
        done in a websocket way and faster, updates the self.positionSoFar,
        self.cash, and self.expectedPosition"""
        if m is not None:
            self.orders[m["standingId"]] = m
            filled = m["filled"]
            price = m["price"]
            direction = m["order"]["direction"]
            qty = m["order"]["qty"] + filled
            """
            for x in self.orders:
                o = self.orders[x]
                # print o
                # direction = o["order"]["direction"]
                # totalFilled = o["order"]["totalFilled"]
                # filled = o["order"]["filled"]
                # price = o["order"]["price"]
                # qty = o["order"]["qty"] + filled
                
                if direction == "sell":
                    # totalFilled = totalFilled * -1
                    filled = filled * -1
                    qty = qty * -1
                self.positionSoFar += filled
                self.expectedPosition += qty
                # -.01 because we are getting the correct unit
                self.cash += totalFilled * price * (-.01)
            """
            if direction == "sell":
                # totalFilled = totalFilled * -1
                filled = filled * -1
                qty = qty * -1
            self.positionSoFar += filled
            self.expectedPosition += qty
            # -.01 because we are getting the correct unit
            self.cash += filled * price * (-.01)
            print "WS - current pos is %d and cash $%d" % (self.positionSoFar, self.cash)
     
        else:
            print "...restarting websocket..."
            self.execution_venue_ticker(self.execution_socket)
            pass

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
        return response.json()

    def delete_order(self, s, o_id):
        full_url = "%s/venues/%s/stocks/%s/orders/%s/cancel" % (self.base_url, self.venues, s, o_id)
        response = requests.post(full_url, headers=self.header)
        return response.json()

    def get_quote(self, s):
        # Get last quote.
        full_url = "%s/venues/%s/stocks/%s/quote" % (self.base_url, self.venues, s)
        response = requests.get(full_url, headers=self.header)
        return response.json()

    def quote_venue_ticker(self, callback):
        def wrapper(msg):
            
            if msg is None:
                callback(None)
            else:
                # msg=json.loads(msg.data)
                callback(msg['quote'])

        url = 'wss://api.stockfighter.io/ob/api/ws/%s/venues/%s/tickertape/stocks/%s' % (self.account, self.venues, self.tickers)
        self.SFSocket(url, wrapper)

    def execution_venue_ticker(self, callback):
        def wrapper(msg):
            
            if msg is None:
                callback(None)
            else:
                # msg=json.loads(msg)
                callback(msg)

        url = 'wss://api.stockfighter.io/ob/api/ws/%s/venues/%s/executions/stocks/%s' % (self.account, self.venues, self.tickers)
        self.SFSocket(url, wrapper)


    class SFSocket(WebSocketClient):
        # with template from jchristma/Stockfighter.

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
