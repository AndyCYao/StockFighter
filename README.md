# StockFighter
References used and good readings on Stockfighter 
http://www.investopedia.com/ask/answers/06/quoteorderdrivenmarket.asp
http://www.investopedia.com/terms/o/order-book.asp

To Do List:
	-Possible bugs in FourthTradeMT
		A.) buy limit orders seems to be cancelled immediately after placed by the CheckFill class.
			probably has to do with the cash.
		B.) the CurrentStatus doesnt produce the same NAV as the execution socket NAV. better to run the same script in thirdTradeTest sell_side, because they have an indicator there to tell us. 
		turns out execution websocket is more accurate. because it calcaultes individual fill and their price.

	-Implement in fourthTradeMT an outlier checker, if impending outlier, cancel everything in the opposition position. ie. 
		Outlier in AskDepth, cancel all the existing buy orders (as they would be filled super quickly). 
		Outlier in BidDepth, cancel all the existing sell orders. 
	

	-DONE Quotesocket sends msgs even when there are changes unseen in the quotes themselves. such as failed 	FOK or cancel orders on closed. so need to make a checker in the quotesocket client for it.
	-Done in the sd.py, finish up the outliers checker in the bid depth and ask depth.
	-DONE Also, lastTrade in the quote socket needs to be a scatter plot rather than compare against the quoteTime because lastTrade has a lastTrade time.