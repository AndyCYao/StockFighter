#!/usr/bin/python

import gviz_api
import json
import datetime
from dateutil import tz, parser

page_template = """
<html>
  <script src="https://www.google.com/jsapi" type="text/javascript"></script>
  <script>
        google.load('visualization', '1', {packages:['corechart']});

        google.setOnLoadCallback(drawTable);
        function drawTable() {
            %(jscode)s
        var jscode_table = new google.visualization.ComboChart(document.getElementById('table_div_jscode'));

        var columns = [];
        var series = {};
        for (var i = 0; i < jscode_data.getNumberOfColumns(); i++) {
            columns.push(i);
            if (i < 4) {
                series[i - 1] = {targetAxisIndex:0, pointSize:5, lineWidth:0};    //index 0 is the price axes
            }
            else if(i <=5 ){
                series[i - 1] = {targetAxisIndex:1, type:'bars'};    //index 1 is the depth axes
            }
        }
        
        var options = {
        'title':'Post-Mordem Analyze', 
        'width':5000, 
        'height':800,
        'pointSize': 1,
        'series': series,
        vAxes:{
            0:{'title': 'Price'},
            1:{'title': "Depth"}
            }
        };

        jscode_table.draw(jscode_data, options);
            //based on http://jsfiddle.net/Khrys/5SD27/
         google.visualization.events.addListener(jscode_table, 'select', function () {
                //alert("something's selected");
                var sel = jscode_table.getSelection();
                // if selection length is 0, we deselected an element
                if (sel.length > 0) {
                    // if row is undefined, we clicked on the legend
                    if (sel[0].row === null) {
                        var col = sel[0].column;
                        if (columns[col] == col) {
                            // hide the data series
                            columns[col] = {
                                label: jscode_data.getColumnLabel(col),
                                type: jscode_data.getColumnType(col),
                                calc: function () {
                                    return null;
                                }
                            };
                            
                            // grey out the legend entry
                            series[col - 1].color = '#CCCCCC';
                        }
                        else {
                            // show the jscode_data series
                            columns[col] = col;
                            series[col - 1].color = null;
                        }
                        var view = new google.visualization.DataView(jscode_data);
                        view.setColumns(columns);
                        jscode_table.draw(view, options);
                    }
                }
            });
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
    <H3>%(infos)s</H3>
    <H4>%(printed)s Table created using gviz_api</H4>
  </body>
</html>
"""


def main():
    """Creating the data - based on this below
    https://developers.google.com/chart/interactive/docs/gallery/linechart#curving-the-lines
    last and lastTime need to be handled differently
    """      
    description = {"quoteTime": ("string", "QuoteTime"), 
                   "bid": ("number", "Best Bid"),
                   "last": ("number", "Last Traded Price"),
                   "ask": ("number", "Best Ask"),
                   "bidDepth": ("number", "Bid Depth"),
                   "askDepth": ("number", "Ask Depth")}
    data = []
    prev_last_trade = None    
    file = json.loads(open("REsultQuoteSocket.json").read())
    local = tz.tzlocal()

    for x in file:
        if "bid" in x:
            bid = x["bid"]
        else:
            bid = None
        if "ask" in x:
            ask = x["ask"]
        else:
            ask = None
        
        utc_lastTrade = parser.parse(x['lastTrade'])
        utc_quoteTime = parser.parse(x['quoteTime'])
        local_lastTrade = utc_lastTrade.astimezone(local)
        local_quoteTime = utc_quoteTime.astimezone(local)

        if local_lastTrade == local_quoteTime:
            file_dict = {"quoteTime": x["quoteTime"], "bid": bid, "last": x['last'], "ask": ask, 
                         "bidDepth": x["bidDepth"], "askDepth": x['askDepth']}            
            prev_last_trade = local_lastTrade
        else:
            if prev_last_trade == local_lastTrade:  # meaning no new trades
                file_dict = {"quoteTime": local_quoteTime, "bid": bid, "last": None, "ask": ask, 
                             "bidDepth": x["bidDepth"], "askDepth": x['askDepth']}
            else:
                #  file_dict = {"quoteTime": prev_last_trade, "bid": None, "last": x["last"], "ask": None, 
                #             "bidDepth": None, "askDepth": None}
                file_dict = {"quoteTime": local_quoteTime, "bid": bid, "last": x['last'], "ask": ask, 
                             "bidDepth": x["bidDepth"], "askDepth": x['askDepth']}                               
                prev_last_trade = local_lastTrade
            
        data.append(file_dict)            

    # need a list of dictionaries.
    # print data
    # Loading it into gviz_api.DataTable
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    
    # Create a JavaScript code string.
    jscode = data_table.ToJSCode("jscode_data",
                                 columns_order=("quoteTime", "last", "ask", "bid", "askDepth", "bidDepth"),
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
