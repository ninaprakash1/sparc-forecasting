from datetime import datetime
from io import StringIO
import pandas as pd
import requests
import logging


WEATHER_API_URL   = "https://stanford-cs329s.github.io/"
WEATHER_DATA_NAME = "weather_data.csv"
MIX_TODAY_API     = "https://www.caiso.com/outlook/SP/fuelsource.csv?_=1643836188083"
MIX_GENERAL_API   = ""
MIX_DATA_NAME     = "mix_data.csv"


def get_updated_weather_data():
    """ Function to hit weather api """
    weather_data = pd.read_csv(WEATHER_DATA_NAME)
    timestamp = weather_data.get('timestamp')
    
    # # Logic for re-querying weather API
    # if timestamp and timestamp - datetime.now().datetime() > 60:
    logging.info("Updating weather data")
    r = requests.get(WEATHER_API_URL)
    logging.info(f"Weather API returned: {r}")
    
    new_data = pd.DataFrame()  # This should read from API
    weather_data = pd.concat([new_data, weather_data]).drop_duplicates().reset_index(drop=True)
    # Update static store of data
    weather_data.to_csv(WEATHER_DATA_NAME)
    
    return weather_data


def get_updated_mix_data():
    """ Function to hit caiso generation mix api """
    mix_data  = pd.read_csv(MIX_DATA_NAME)
    timestamp = datetime.strptime(mix_data.iloc[-1]['Time'], "%H:%M")
    
    # Logic for re-querying weather API
    # if timestamp - datetime.now().time() > 5:

    logging.info("Updating generation mix data")
    r = requests.get(MIX_TODAY_API)
    data = StringIO(str(r.text))
    # logging.info(f"Caiso API returned (first 100): {data[:100]}")

    new_data = pd.read_csv(data)
    mix_data = pd.concat([new_data, mix_data]).drop_duplicates().reset_index(drop=True)
    # Update static store of data
    mix_data.to_csv(MIX_DATA_NAME)
    
    return mix_data