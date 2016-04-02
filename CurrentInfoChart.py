#!/usr/bin/python

import gviz_api

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
  <body>
    <H1>Table created using ToJSCode</H1>
    <div id="table_div_jscode"></div>
  </body>
</html>
"""

def main():
  # Creating the data - based on this below
  # https://developers.google.com/chart/interactive/docs/gallery/linechart#curving-the-lines
  """
  description = {"time": ("date", "time"),
                 "lastQuote": ("number", "lastQuote"),
                }
  data = [{"time": "Mike", "salary": (10000, "$10,000"), "full_time": True},
          {"time": "Jim", "salary": (800, "$800"), "full_time": False},
          {"time": "Alice", "salary": (12500, "$12,500"), "full_time": True},
          {"time": "Bob", "salary": (7000, "$7,000"), "full_time": True}]

  # Loading it into gviz_api.DataTable
  data_table = gviz_api.DataTable(description)
  data_table.LoadData(data)

  # Create a JavaScript code string.
  jscode = data_table.ToJSCode("jscode_data",
                               columns_order=("name", "salary", "full_time"),
                               order_by="salary")
  # Create a JSON string.
  # json = data_table.ToJSon(columns_order=("name", "salary", "full_time"),
                           # order_by="salary")

  # Put the JS code into the template.
  print "Content-type: text/html" 
  print page_template % vars()
  """

if __name__ == '__main__':
  main()