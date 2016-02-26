"""Contains GameMaster and Stockfighter."""
import requests
import json


class GameMaster:
    """Contains the codes necessary to start the instance."""

    base_url = "https://api.stockfighter.io/ob/api"
    gm_url = "https://www.stockfighter.io/gm"

    def __init__(self):
        pass

    def get_current_venue(self):
        pass

    def get_current_stock(self):
        pass
            
    def get_current_account(self):
        pass

    def get_api_key(self):
        file = open('apikey.txt', 'r')
        apikey = file.readlines()[0]
        return apikey

    def get_instance_id(self):
        # header = "Cookie:api_key=%s" % (self.get_api_key())
        # header = "%s" % (self.get_api_key())
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
            return response
        except ValueError as e:
            return{'error': e, 'raw_content': response.content}


class StockFighter:
    """Contains the methods neccessary to make API calls."""

    def __init__(self, LevelName):
        gm = GameMaster()
        apikey = gm.get_api_key()
        response = gm.post_level(LevelName)

        self.base_url = "https://api.stockfighter.io/ob/api"
        self.account = response.json().get("account")
        self.instanceID = response.json().get("instanceId")
        self.venues = ''.join(response.json().get("venues"))
        self.tickers = ''.join(response.json().get("tickers"))
        self.header = {'X-Starfighter-Authorization': apikey}
        print "venue is %s , account is %s, id %s, ticker %s" %(self.venues,self.account,self.instanceID,self.tickers)
        # further research at https://discuss.starfighters.io/t/the-gm-api-how-to-start-stop-restart-resume-trading-levels-automagically/143

    def get_order_book(self, s):
        """retrieve the order book"""
        full_url = "%s/venues/%s/stocks/%s" % (self.base_url, self.venues, s)
        response = requests.get(full_url, headers=self.header)
        return response

    def read_orderbook(self, oBook, direction, type):
        try:
            best_result = oBook.json().get(direction)[0].get(type)
        except (RuntimeError, TypeError, NameError):
            best_result = 0
        return best_result

    def fill_confirmation(self, s, id):
        """return total number filled for this specific id"""
        full_url = "%s/venues/%s/stocks/%s/orders/%s" % (self.base_url, self.venues,s,id)
        response = requests.get(full_url, headers=self.header)
        # print response.json()
        return response.json().get('totalFilled'), \
            response.json().get('direction'), \
            response.json().get('open')

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

    def get_quote(self, s):
        # Get last quote 
        full_url = "%s/venues/%s/stocks/%s/quote" % (self.base_url, self.venues, s)
        response = requests.get(full_url, headers=self.header)
        last = response.json()
        return last


    