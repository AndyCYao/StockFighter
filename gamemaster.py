"""Contains GameMaster and Stockfighter."""
import requests
import json


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
    
    """
    def write_to_setting(self, responseJSON):
            # store the current session into file to retrieve
            # for restart, resume etc. 

        with open("currentInfo.json", "w") as settings:
            json.dump(responseJSON, settings)
        settings.close()
    """
    

class StockFighter:
    """Contains the methods neccessary to make API calls."""

    def __init__(self, LevelName):
        gm = GameMaster()
        apikey = gm.get_api_key()
        # look in the currentinfo, if exists check if its active
        # if active prompt user if they want to restart or new
        
        """
        info = open("currentInfo.json", "r")
        current_info = json.load(info)
        x = raw_input("Would you like to restart previous stored level? Y/N ->")

        if current_info["ok"] and x.upper() == "Y":
            prev_id = current_info["instanceId"]
            response = gm.restart_level(prev_id)
            info.close()
        else:
        """
        response = gm.post_level(LevelName)

        self.base_url = "https://api.stockfighter.io/ob/api"
        self.account = response.json().get("account")
        self.instanceID = response.json().get("instanceId")
        self.venues = ''.join(response.json().get("venues"))
        self.tickers = ''.join(response.json().get("tickers"))
        self.header = {'X-Starfighter-Authorization': apikey}
        print "venue is %s , account is %s, id %s, ticker %s" % (self.venues, self.account, self.instanceID, self.tickers)
        # further research at https://discuss.starfighters.io/t/the-gm-api-how-to-start-stop-restart-resume-trading-levels-automagically/143

    def status_for_all_orders_in_stock(self, s):
        """ retrieve all orders given account """
        full_url = "%s/venues/%s/accounts/%s/stocks/%s/orders" % (self.base_url, self.venues, self.account, s)
        response = requests.get(full_url, headers=self.header)
        return response

    def get_order_book(self, s):
        """retrieve the order book"""
        full_url = "%s/venues/%s/stocks/%s" % (self.base_url, self.venues, s)
        response = requests.get(full_url, headers=self.header)
        return response

    def read_orderbook(self, oBook, direction, type):
        """this returns the best price of buy or sell """
        try:
            best_result = oBook.json().get(direction)[0].get(type)
        except (RuntimeError, TypeError, NameError):
            best_result = 0
        return best_result

    def update_open_orders(self, orderList):
        """loops through the open ids and check them see.
        how many have been filled. i am changing it to loop through the orders from.
        status_for_all_orders_in_stock
        """
        currentPos = 0
        currentPosCash = 0
        expectedPos = 0
        for x in orderList["orders"]:
            # o_id = x["id"]
            totalFilled = x["totalFilled"]
            originalQty = x["originalQty"]
            direction = x["direction"]
            price = x["price"]
           
            if direction == "sell":
                totalFilled = totalFilled * -1
                originalQty = originalQty * -1
                
            currentPos += totalFilled
            expectedPos += originalQty
            # -.01 because we are getting the correct unit
            currentPosCash += totalFilled * price * (-.01)

        # print "current pos is %d and $%d" %(currentPos, currentPosCash)
        return currentPos, currentPosCash, expectedPos

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
        # Get last quote.
        full_url = "%s/venues/%s/stocks/%s/quote" % (self.base_url, self.venues, s)
        response = requests.get(full_url, headers=self.header)
        last = response.json()
        return last


    