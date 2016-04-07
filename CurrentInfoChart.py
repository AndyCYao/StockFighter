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
        'pointSize': 1,
        'series': series
        };

        jscode_table.draw(jscode_data, options);
        var columns = [];
        var series = {};
        for (var i = 0; i < jscode_data.getNumberOfColumns(); i++) {
            columns.push(i);
            if (i > 0) {
                series[i - 1] = {};
            }
        }
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

"""
        var columns = {1: true, 2: true, 3: true}; 
        // 0 is last, 1 is ask, 2 is bid. the value is whether to display or not
        //var LastHidden = false;
        var hideLast = document.getElementById("hideLast");
        hideLast.onclick = function()
           {
                columns[1] = !columns[1]
                ShowHide();
           }
        var AskHidden = false;
        var hideAsk = document.getElementById("hideAsk");
        hideAsk.onclick = function()
           {
                columns[2] = !columns[2];
                ShowHide();
           }
        var BidHidden = false;
        var hideBid = document.getElementById("hideBid");
        hideBid.onclick = function()
           {
                columns[3] = !columns[3];
                ShowHide();
           }

        //hiden columns base on the column dictionary and redraw the table
        function ShowHide(){
              view = new google.visualization.DataView(jscode_data);
              for (var x in columns){
                if (columns[x] == false){
                  //alert("columns[" + x + "] is " + columns[x]);
                  y = parseInt(x)
                  view.hideColumns([y]);
                }
              }
              jscode_table.draw(view, options);
        }
"""
