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

def return_best_price(oBook):
    try:
        BestAsk = oBook.json().get('asks')[0].get('price')
        BestAskQty = oBook.json().get("asks")[0].get('qty')
    except (RuntimeError, TypeError, NameError): 
        BestAsk = 0
        BestAskQty = 0

    return BestAsk, BestAskQty

def fill_confirmation(v,s,id):
    full_url = "%s/venues/%s/stocks/%s/orders/%s" %(base_url,v,s,id)
    response = requests.get(full_url,headers= header)
    # print response.json()
    return response.json().get('ok')

def buy_stock(v, p, q, s):
    order = {
        "account": account,
        "venue": venues,
        "symbol": s,
        "price": p,
        "qty": q,
        "direction": "buy",
        "orderType": "limit"
    }
    full_url = "%s/venues/%s/stocks/%s/orders" % (base_url, v, s)
    response = requests.post(full_url, headers=header, data=json.dumps(order))
    return response.json()

def get_quote(s):
    # Get last quote 
    full_url = "%s/venues/%s/stocks/%s/quote" % (base_url, venues, s)
    response = requests.get(full_url, headers=header)
    # last = response.json().get('last')
    last = response.json()
    return last




start = time.time()
end  = time.time()
totalGoal = 2000
lastQuote = get_quote(tickers)
lastQuotePrice = lastQuote.get('last')
print "Last Quote %s" %(lastQuotePrice)


buyOrder = buy_stock(venues, lastQuotePrice,100,tickers)
# print "Print Buy Order %s" %(buyOrder)
buyID = buyOrder.get('id')
buyPrice = buyOrder.get('price')

print "bought at %s" %(buyPrice)
print "check fill status - ID %s" %(buyID)
print "confirmed fill - %s " %(fill_confirmation(venues,tickers,buyID))

q = 1000
while totalGoal > 0 and (end - start) < 120:
    time.sleep(5)
    BestAsk , q = return_best_price(get_order_book(venues,tickers)) # best asking price
    

    buyOrder = buy_stock(venues, BestAsk,q,tickers)
    # print "Print Buy Order %s" %(buyOrder)
    buyID = buyOrder.get('id')
    buyPrice = buyOrder.get('price')
    print "check fill status - ID %s" %(buyID)
    
    fillResults = fill_confirmation(venues,tickers,buyID)
    if fillResults:
        print "bought at %s" %(buyPrice)
        totalGoal -= q
    print "confirmed fill - %s " %(fillResults)
    end  = time.time()
    print(end - start)
