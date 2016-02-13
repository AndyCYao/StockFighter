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

def buy_confirmation():
    pass


def buy_stock(p, q, s):
    order = {
        "account": account,
        "venue": venues,
        "symbol": s,
        "price": p,
        "qty": q,
        "direction": "buy",
        "orderType": "limit"
    }
    full_url = "%s/venues/%s/stocks/%s/orders" % (base_url, venues, s)
    response = requests.post(full_url, headers=header, data=json.dumps(order))
    print(response.text)


def get_quote(s):
    # Get last quote 
    full_url = "%s/venues/%s/stocks/%s/quote" % (base_url, venues, s)
    response = requests.get(full_url, headers=header)
    last = response.json().get('last')
    return last

totalGoal = 1500
lastQuote = get_quote(tickers)

print "Last Quote %s" %(lastQuote)
print buy_stock(lastQuote,100,tickers)


while totalGoal > 0:
    time.sleep(3)
    print(get_quote(tickers))
    Diff = abs((get_quote(tickers) - lastQuote) / lastQuote)
    print "current different %d" % (Diff)

    if Diff < .05:
        q = 100
        buy_stock(lastQuote, q, tickers)
        totalGoal -= q
