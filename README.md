# spreadhseet2influx

Keeps in sync timeseries stored in Google spreadsheet and Influx databases.

Use case:
* Create a Google form
* Make questions support multiple numerical options
* Submit a response once in a while
* Responses will be sent to a Spreadsheet, and spreadsheet2influx syncs them
with Influx
* Create a Grafana visualization of the temporal evolution of the responses
