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
      jscode_table.draw(jscode_data, {showRowNumber: true});
    }
  </script>
  <style type="text/css">
    HTML{
        font-family:arial
    }

  </style>
  <body>
    <H2>%(infos)s</H2>
    <div id="table_div_jscode"></div>
    <H4>%(printed)s Table created using gviz_api</H4>
  </body>
</html>
"""

def main():
    # Creating the data - based on this below
    # https://developers.google.com/chart/interactive/docs/gallery/linechart#curving-the-lines
      
    description = {"quoteTime": ("string", "QuoteTime"), "last": ("number", "Last Traded Price")}
    data = []
    file = json.loads(open("currentInfo.json").read())
    for x in file:
        file_dict = {"quoteTime": x["quoteTime"], "last": x["last"]}
        data.append(file_dict)

    # need a list of dictionaries.
    # print data
    # Loading it into gviz_api.DataTable
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    
    # Create a JavaScript code string.
    jscode = data_table.ToJSCode("jscode_data",
                                 columns_order=("quoteTime", "last"),
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
