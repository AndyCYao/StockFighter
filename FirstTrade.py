import requests
import json

base_url = "https://api.stockfighter.io/ob/api"
apikey = "42390651814d1884728dfe6dea41545b2bdb5f09"
account = 'HHT42126805'
venue = 'IFUEX'
stock = 'TYEY'

order = {
    "account": account,
    "venue": venue,
    "symbol": stock,
    "price": 6000,
    "qty": 100,
    "direction": "buy",
    "orderType": "limit"
}

auth = {'X-Starfighter-Authorization': apikey}
full_url = "%s/venues/%s/stocks/%s/orders" % (base_url, venue, stock)

response = requests.post(full_url, headers=auth, data=json.dumps(order))

print(response.text)
