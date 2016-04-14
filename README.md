# StockFighter
References used and good readings on Stockfighter 
http://www.investopedia.com/ask/answers/06/quoteorderdrivenmarket.asp
http://www.investopedia.com/terms/o/order-book.asp

To Do List:
	-DONE Quotesocket sends msgs even when there are changes unseen in the quotes themselves. such as failed FOK
	or cancel orders on closed. so need to make a checker in the quotesocket client for it.
	-in the sd.py, finish up the outliers checker in the bid depth and ask depth.
	-DONE Also, lastTrade in the quote socket needs to be a scatter plot rather than compare against the quoteTime
	because lastTrade has a lastTrade time.