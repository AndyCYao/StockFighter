import requests

base_url = "https://api.stockfighter.io/ob/api/heartbeat"

r = requests.get(base_url)
print(r.text)