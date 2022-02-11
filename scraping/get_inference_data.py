import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from io import StringIO
import pandas as pd
from tqdm import tqdm
import time
from wwo_hist import retrieve_hist_data

def get_day_strings(n):
    """
    @param      n               Number of historical days starting from today
    @return     day_strings     List of strings in %Y%m%d format for CAISO request representing
                                most recent n days 
                start_date      String representing the date of n days ago in %d-%month-%Y format
                                for wwo_hist request
                end_date        String representing today's date in %d-%month-%Y format for wwo_hist
                                request
    """
    today = datetime.now(timezone('US/Pacific'))
    
    day_strings = []
    day_strings.append(str(today.year) + ('0' + str(today.month))[-2:] + ('0' + str(today.day))[-2:])
    end_date = ('0' + str(today.day))[-2:] + '-' + today.strftime("%b").upper() + '-' + str(today.year)

    hours_remaining = 24*n - today.hour - 1
    while (hours_remaining > 0):
        yesterday = today - timedelta(days=1)
        day_strings.append(str(yesterday.year) + ('0' + str(yesterday.month))[-2:] + ('0' + str(yesterday.day))[-2:])
        hours_remaining -= 24
        today = yesterday
    start_date = ('0' + str(today.day))[-2:] + '-' + today.strftime("%b").upper() + '-' + str(today.year)
        
    return day_strings[::-1], start_date, end_date

def get_suppy_data(day):
    """
    @param      day     String formatted in %Y%m%d to make request to CAISO
    @return     csv     Dataframe of generation mix data on given day
    """
    caiso = 'http://www.caiso.com/outlook/SP/History/'

    r = requests.get(f"{caiso}{day}/fuelsource.csv?_=1642727187499")
    soup = bs(r.text, 'html.parser')
    csv = StringIO(str(soup))
    
    return csv

def get_weather_data(start_date, end_date, api_key):
    hist_weather_data = retrieve_hist_data(api_key,
                                ['california'],
                                start_date,
                                end_date,
                                1,
                                location_label = False,
                                export_csv = False,
                                store_df = True)[0]
    return hist_weather_data

def get_genmix_data(day_strings, n):
    all_df = pd.DataFrame()
    for day in tqdm(day_strings):
        data = get_suppy_data(day)
        new_df = pd.read_csv(data, sep=",")
        new_df['Day'] = [day for r in range(len(new_df['Time']))]
        all_df = pd.concat([all_df, new_df])
        time.sleep(0.1)
        
    # 3. Filter only last n * 24 hours
    genmix_data = all_df.tail(int(n * 24 * 60 / 5))
    return genmix_data

def merge_data(genmix_data, weather_data):
    """
    Combine generation mix and weather data, joining by datetime.
    Resample weather_data (hourly frequency) to match 5-minute frequency
    of genmix_data.

    @param  genmix_data     Dataframe representing generation mix for last n days
    @param  weather_data    Dataframe representing weather data for last n days
    @return full_data       Dataframe merged by datetime
    """
    genmix = genmix_data.astype({'Day':str,'Time':str})
    weather = weather_data.rename(columns={'date_time':'date_time_hourly'})

    # Add datetime column to generation mix data
    genmix['date_time_5min'] = genmix.Day + " " + genmix.Time
    genmix.date_time_5min = pd.to_datetime(genmix.date_time_5min)
    genmix['date_time_hourly'] = genmix.date_time_5min.dt.floor('h')
    genmix = genmix[['date_time_hourly','date_time_5min','Solar','Wind','Geothermal','Biomass','Biogas','Small hydro','Coal','Nuclear','Batteries','Imports','Other','Natural Gas','Large Hydro']]

    # Define weather columns to keep
    weather_cols = ['date_time_hourly','tempC', 'uvIndex','WindGustKmph','cloudcover','humidity','precipMM']
    weather = weather[weather_cols]

    # Join data by datetime
    full_data = genmix.merge(weather.set_index('date_time_hourly'),on='date_time_hourly',how='inner')

    return full_data

def get_last_n_days(n):
    """
    Main function to gather and merge all inference data for n historical days
    in 5-minute frequency for generation mix data and 1-hour frequency resampled
    to 5-minute frequency for weather data.
    
    @param      n              Number of historical days 
    @return     last_n_days    Dataframe of generation mix and weather data for past n days
    """
    # 1. Get list of days representing the last n * 24 hours from current hour
    day_strings, start_date, end_date = get_day_strings(n)
    
    # 2. Get generation mix data from CAISO
    genmix_data = get_genmix_data(day_strings, n)

    # 3. Get weather data
    api_key = '8d0e4b3d61f149e095124908222101'
    weather_data = get_weather_data(start_date, end_date, api_key)
    
    # 4. Merge genmix and weather data
    last_n_days = merge_data(genmix_data, weather_data)
    
    return last_n_days