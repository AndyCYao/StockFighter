import requests
import json
import gamemaster
import time

base_url = "https://api.stockfighter.io/ob/api"

gm = gamemaster.GameMaster()

apikey = gm.get_api_key()
response =  gm.post_level("chock_a_block")
account = response.json().get("account")
instanceID = response.json().get("instanceId")
venues = ''.join(response.json().get("venues"))
tickers = ''.join(response.json().get("tickers"))
header = {'X-Starfighter-Authorization': apikey}

print "venue is %s , account is %s, id %s, ticker %s" %(venues,account,instanceID,tickers)
# further research at https://discuss.starfighters.io/t/the-gm-api-how-to-start-stop-restart-resume-trading-levels-automagically/143

def get_order_book(v,s):
    full_url = "%s/venues/%s/stocks/%s" %(base_url,v,s)
    response = requests.get(full_url, headers= header)
    return response


oBook = get_order_book(venues,tickers)
print oBook
print oBook.json().get("asks")[0]
print oBook.json().get("asks")[0].get('price')
print oBook.json().get("asks")[0].get('qty')