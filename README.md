# StockFighter
References used and good readings on Stockfighter 
http://www.investopedia.com/ask/answers/06/quoteorderdrivenmarket.asp
http://www.investopedia.com/terms/o/order-book.asp

To Do List:
	-Done -add timestamp on all the print out messages. 

	the below bugs almost seems like for every trade. i need to check a position, i cant just do 1 check, and make 3 orders out of it. espceially when i am working with such a wide margin of quantity at a time.
	propose doing a check everytime theres a new change.

	-Bug- noticed that sometimes the BuySell would not have the most updated positionSoFar, as the execution websocket had updated it by the time BuySell calls it. need to find a better way to track everything.
	-Bug -the alreadyBought and alreadySold arnt always accurate. an order would be showing up at one time, but later it wouldnt, but the execution ticker wouldnt hav eupdate it.
	-Implement a way to examin the orderbook and filter out the orders that are from myself.

	Done A.) buy limit orders seems to be cancelled immediately after placed by the CheckFill class.
		probably has to do with the cash. 
		this was because of bug in checkign the timestamp of order with current UTC time. i have disable it because doesn't work

	Done B.) the CurrentStatus doesnt produce the same NAV as the execution socket NAV. better to run the same script in thirdTradeTest sell_side, because they have an indicator 		  there to tell us. 
			turns out execution websocket is more accurate. because it calcaultes individual fill and their price.

	-DONE Quotesocket sends msgs even when there are changes unseen in the quotes themselves. such as failed 	FOK or cancel orders on closed. so need to make a checker in the quotesocket client for it.
	-Done in the sd.py, finish up the outliers checker in the bid depth and ask depth.
	-DONE Also, lastTrade in the quote socket needs to be a scatter plot rather than compare against the quoteTime because lastTrade has a lastTrade time.