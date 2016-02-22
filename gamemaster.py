import requests
import json
# import stockfighter

class GameMaster(object):

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
        file = open('apikey.txt','r')
        apikey  = file.readlines()[0]
        
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

    def post_level(self,level):
        header = {'X-Starfighter-Authorization': self.get_api_key()}
        full_url = "%s/levels/%s" % (self.gm_url, level)
        response = requests.post(full_url, headers=header)

        try:
            return response
        except ValueError as e:
            return{'error': e, 'raw_content': response.content}


