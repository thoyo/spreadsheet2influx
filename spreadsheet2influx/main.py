from dotenv import load_dotenv
import os
import logging
from influxdb import InfluxDBClient
import time
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import json

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Starting program")

INFLUX_PORT = 8086
INFLUX_DATABASE = "spreadsheets"
if os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False):
    INFLUX_HOST = "influxdb_mt"
else:
    INFLUX_HOST = "0.0.0.0"

INFLUXDBCLIENT = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DATABASE)

load_dotenv()

# TODO: don't hardcode it, create API and support sending new IDs
SPREADSHEET_IDS = json.loads(os.getenv("SPREADSHEET_IDS"))


def get_data_from_spreadsheet(spreadsheet_id):
    credentials = Credentials.from_service_account_file("service_account.json",
                                                        scopes=['https://spreadsheets.google.com/feeds'])
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.sheet1
    return worksheet.get_all_values()


def write_data_to_influx(data):
    df = pd.DataFrame(data[1:], columns=data[0])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d/%m/%Y %H:%M:%S')

    # Get the schema
    columns_types = {}
    for index, row in df.iterrows():
        for column, value in row.items():
            if column == "Timestamp":
                continue
            existing_column_type = columns_types.get(column)
            try:
                if value != "":
                    _ = float(value)
                # It's a float!
                if existing_column_type is None:
                    columns_types[column] = "float"
            except ValueError:
                # It's a string!
                if existing_column_type is None or existing_column_type == "float":
                    columns_types[column] = "string"

    # Write the data
    influx_data = []
    for index, row in df.iterrows():
        fields = {"event": 1}
        tags = {}
        for column, value in row.items():
            if column == "Timestamp" or value == "":
                continue
            if columns_types[column] == "string":
                tags[column] = value
            else:
                fields[column] = float(value)
        point = {
            "measurement": "orella",
            "time": row["Timestamp"].strftime('%Y-%m-%dT%H:%M:%SZ'),
            "fields": fields,
            "tags": tags
        }
        influx_data.append(point)

    # TODO: query influx to get latest datapoint and only insert newer ones
    # TODO: write in a measurement with the name of the spreadsheet
    INFLUXDBCLIENT.write_points(influx_data)


def main():
    for spreadsheet_id in SPREADSHEET_IDS:
        data = get_data_from_spreadsheet(spreadsheet_id)
        write_data_to_influx(data)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(e, exc_info=True)
        time.sleep(60)
