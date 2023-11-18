from dotenv import load_dotenv
import os
import logging
from influxdb import InfluxDBClient, DataFrameClient
import time
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

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

INFLUXDBCLIENT = DataFrameClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DATABASE)

load_dotenv()

# TODO: don't hardcode it, create API and support sending new IDs
SPREADSHEET_ID = '1_rUbAoVubKcX8SOs9oGiL2Urwhk2vEFHO7SS87HYtIs'


def get_data_from_spreadsheet():
    credentials = Credentials.from_service_account_file("service_account.json", 
                                                        scopes=['https://spreadsheets.google.com/feeds'])
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.sheet1
    return worksheet.get_all_values()


def write_data_to_influx(data):
    df = pd.DataFrame(data[1:], columns=data[0])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d/%m/%Y %H:%M:%S')
    df.set_index('Timestamp', inplace=True)
    df[df.columns.difference(['Timestamp'])] = df[df.columns.difference(['Timestamp'])].apply(pd.to_numeric, errors='coerce')
    # TODO: query influx to get latest datapoint and only insert newer ones
    INFLUXDBCLIENT.write_points(df, "orella", protocol="line")


def main():
    data = get_data_from_spreadsheet()
    write_data_to_influx(data)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(e, exc_info=True)
        time.sleep(60)
