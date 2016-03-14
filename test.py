import time
import gamemaster
import json

# print "Trying Test.."
# sf = gamemaster.StockFighter.test_mode()

print "Try actual level"
sf = gamemaster.StockFighter("dueling_bulldozers")

with open("currentInfo.json", "w") as settings:
    while 1:
        time.sleep(.5)
        oBook = sf.get_order_book(sf.tickers).json()
        # print oBook.json()
        # settings.write(oBook.json())
        json.dump(oBook, settings)
settings.close()