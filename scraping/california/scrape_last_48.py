import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from io import StringIO
import pandas as pd
from tqdm import tqdm
import time

def get_day_strings():
    
    today = datetime.now(timezone('US/Pacific'))
    
    day_strings = []
    day_strings.append(str(today.year) + ('0' + str(today.month))[-2:] + ('0' + str(today.day))[-2:])
    
    hours_remaining = 48 - today.hour - 1
    while (hours_remaining > 0):
        yesterday = today - timedelta(days=1)
        day_strings.append(str(yesterday.year) + ('0' + str(yesterday.month))[-2:] + ('0' + str(yesterday.day))[-2:])
        hours_remaining -= 24
        today = yesterday
        
    return day_strings

def get_suppy_data(day):

    caiso = 'http://www.caiso.com/outlook/SP/History/'

    r = requests.get(f"{caiso}{day}/fuelsource.csv?_=1642727187499")
    soup = bs(r.text, 'html.parser')
    csv = StringIO(str(soup))
    
    return csv

def get_last_48_hours():
    # 1. Get list of days representing the last 48 hours (2 or 3)
    day_strings = get_day_strings()
    
    # 2. Get generation mix data from CAISO
    all_df = pd.DataFrame()

    for day in tqdm(day_strings):
        data = get_suppy_data(day)
        new_df = pd.read_csv(data, sep=",")
        new_df['Day'] = [day for r in range(len(new_df['Time']))]
        all_df = pd.concat([all_df, new_df])
        time.sleep(0.1)
        
    # 3. Filter only last 48 hours
    last_48_hours = all_df.head(int(48 * 60 / 5))
    
    return last_48_hours