#!/usr/bin/python

import gviz_api
import json
import datetime

page_template = """
<html>
  <script src="https://www.google.com/jsapi" type="text/javascript"></script>
  <script>
        google.load('visualization', '1', {packages:['corechart']});

        google.setOnLoadCallback(drawTable);
        function drawTable() {
            %(jscode)s
            var jscode_table = new google.visualization.LineChart(document.getElementById('table_div_jscode'));
            var options = {
            'title':'Post-Mordem Analyze', 
            'width':2000, 
            'height':800,
            'series': {
                1: { lineDashStyle: [2, 2], color: '#ff4000' },
                2: { lineDashStyle: [4, 4], color: '#00ff00' }
                }
            };
        jscode_table.draw(jscode_data, options);
        var columns {0: false, 1: false, 2: false}; // 0 is last, 1 is ask, 2 is bid. the value is whether to display or not
        //var LastHidden = false;
        var hideLast = document.getElementById("hideLast");
        hideLast.onclick = function()
           {
                //LastHidden != LastHidden;

           }
        var AskHidden = false;
        var hideAsk = document.getElementById("hideAsk");
        hideAsk.onclick = function()
           {
                AskHidden != AskHidden;
           }
        var BidHidden = false;
        var hideBid = document.getElementById("hideBid");
        hideBid.onclick = function()
           {
                BidHidden != BidHidden;
           }
        function ShowHide(){
              view = new google.visualization.DataView(jscode_data);
              view.hideColumns([3]); 
              jscode_table.draw(view, options);
        }
    }
  </script>
  <style type="text/css">
    HTML{
        font-family:arial;
        text-align:center
    }

  </style>
  <body>
    <H2>Stockfighter 2016</H2>
    <div id="table_div_jscode"></div>
    <button type="button" id="hideLast"  >Hide Last</button>
    <button type="button" id="hideBid"  >Hide Bid</button>
    <button type="button" id="hideAsk"  >Hide Ask</button>
    <H3>%(infos)s</H3>
    <H4>%(printed)s Table created using gviz_api</H4>
  </body>
</html>
"""

def main():
    # Creating the data - based on this below
    # https://developers.google.com/chart/interactive/docs/gallery/linechart#curving-the-lines
      
    description = {"quoteTime": ("string", "QuoteTime"), 
                   "bid": ("number", "Best Bid"),
                   "last": ("number", "Last Traded Price"),
                   "ask": ("number", "Best Ask")}
    data = []
    file = json.loads(open("currentInfo.json").read())
    for x in file:
        if "bid" in x:
            bid = x["bid"]
        else:
            bid = None
        if "ask" in x:
            ask = x["ask"]
        else:
            ask = None

        file_dict = {"quoteTime": x["quoteTime"], "bid": bid, "last": x["last"], "ask": ask}
        data.append(file_dict)

    # need a list of dictionaries.
    # print data
    # Loading it into gviz_api.DataTable
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    
    # Create a JavaScript code string.
    jscode = data_table.ToJSCode("jscode_data",
                                 columns_order=("quoteTime", "last", "ask", "bid"),
                                 order_by="quoteTime")
    infos = """
        Venue-%s Trading %s.  
    """ % (x["venue"], x["symbol"])
    printed = "printed on %r." % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

    # Put the JS code into the template.
    print "Loading graph.html...", 
    open("Graph.html", 'w').close()  # doing this clears everything first
    with open("Graph.html", "a") as graph:
        graph.write(page_template % vars())
    graph.close()
    print "Done"
if __name__ == '__main__':
    main()

