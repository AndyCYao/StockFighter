# StockFighter
References used and good readings on Stockfighter 
http://www.investopedia.com/ask/answers/06/quoteorderdrivenmarket.asp
http://www.investopedia.com/terms/o/order-book.asp

Fourth Level - Dueling Bulldozers -
	best try so far. 
	Reached NAV $225 before instance time up. 
	Reached NAV $205k before the instance time was up around 2506 secs 41 minutes


To Do List:
	Bug- the self.order got updated before the self.position_so_far did. so the BuySell had incorrect numbers to make decision with, causing losing games.

	Done make sf.positionSoFar , cash, nav expected position in gamemaster private instance variables.
	Done -make all the parameters for each class adjustable in the init of each class.

	-Done Made CheckFill reliant on the self.order rather than check_status_order method to pump out the list of current orders.
	since self.order is kept in memory, rather than check_status_order is a HTTP request. so its much faster and should be accurate.
	-Done make BuySell independent of CurrentStatus, as in take out the queue reliance.
	-Done -add timestamp on all the print out messages. 	
	-Done -the alreadyBought and alreadySold arnt always accurate. an order would be showing up at one time, but later it wouldnt, but the execution ticker wouldnt hav eupdate it. or that it shows no outstanding order, but infact there is. 
		I've solve this by implementing a order dictionary that tracks locally my current orders. 
	
	-Implement a way to examin the orderbook and filter out the orders that are from myself.

	Done A.) buy limit orders seems to be cancelled immediately after placed by the CheckFill class.
		probably has to do with the cash. 
		this was because of bug in checkign the timestamp of order with current UTC time. i have disable it because doesn't work

	Done B.) the CurrentStatus doesnt produce the same NAV as the execution socket NAV. better to run the same script in thirdTradeTest sell_side, because they have an indicator 		  there to tell us. 
			turns out execution websocket is more accurate. because it calcaultes individual fill and their price.

	-DONE Quotesocket sends msgs even when there are changes unseen in the quotes themselves. such as failed 	FOK or cancel orders on closed. so need to make a checker in the quotesocket client for it.
	-Done in the sd.py, finish up the outliers checker in the bid depth and ask depth.
	-DONE Also, lastTrade in the quote socket needs to be a scatter plot rather than compare against the quoteTime because lastTrade has a lastTrade time.