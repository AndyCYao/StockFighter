import time
import gamemaster
import json

# print "Trying Test.."
# sf = gamemaster.StockFighter.test_mode()

print "Try actual level"
sf = gamemaster.StockFighter("dueling_bulldozers")

open("currentInfo.json", 'w').close() # doing this clears everything first

try:
	with open("currentInfo.json", "a") as settings:
	    while 1:
	        time.sleep(2)
	        print "--"
	        oBook = sf.get_order_book(sf.tickers).json()
	        print oBook
	        print "\n"
	        json.dump(oBook, settings)
	settings.close()
except KeyboardInterrupt:
	print "ctrl+c pressed"
	settings.close()