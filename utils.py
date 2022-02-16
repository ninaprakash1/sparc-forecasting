import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from pytz import timezone
import time
import json
from io import StringIO
from tqdm import tqdm
from wwo_hist import retrieve_hist_data


def compute_co2(results, activity, hour):
    """
    @param      results     Dictionary in form {'fossil_fuel': [], 'renewable', [], 'other': []}
                            where each list has length 24 and represents the predicted supply at
                            every hour after end of training data
    @param      activity    One of {"Charge an EV", "Run a load of laundry","Take a hot shower"}
    @param      hour        Time at which to compute CO2 emissions in form as '1:00pm'
    @return     co2         Amount of co2 emissions generated by given activity at given time

    Emissions factor sources:   https://www.epa.gov/sites/default/files/2020-12/documents/power_plants_2017_industrial_profile_updated_2020.pdf
                                https://www.caiso.com/Documents/GreenhouseGasEmissionsTracking-Methodology.pdf
    """

    if activity not in {"Charge an EV", "Run a load of laundry","Take a hot shower"}:
        raise ValueError('activity must be one of {"Charge an EV", "Run a load of laundry","Take a hot shower"}. Received {}'.format(activity))

    # Get forecasted supply results at requested hour
    current_hour = datetime.now(timezone('US/Pacific')).hour # [0, 23]
    if (hour.split(':')[0] == '12' and hour[-2:] == 'am'):
        given_hour = 0
    if (hour.split(':')[0] == '12' and hour[-2:] == 'pm'):
        given_hour = 12
    else:
        given_hour = int(hour.split(':')[0]) + 12 if hour[-2:] == 'pm' else int(hour.split(':')[0])
    hours_until_given_hour = int((datetime.strptime(str(current_hour),'%H') - datetime.strptime(str(given_hour), '%H')).seconds / 3600)

    # Get forecasted generation mix
    #   --> approximating fossil fuel as only natural gas
    #   --> approximating other as only imports
    nat_gas_mwh = results['fossil_fuel'].tolist()[hours_until_given_hour] # need .tolist() if calling locally
    imports_mwh = results['other'].tolist()[hours_until_given_hour]
    renewables_mwh = results['renewable'].tolist()[hours_until_given_hour]
    total_supply = nat_gas_mwh + imports_mwh + renewables_mwh

    # Estimate energy usage
    nat_gas_emissions_factor = 898 * 1e-3 # (lb CO2 / MWh) x (1 MWh / 10^3 kWh) = lb CO2 / kWh
    imports_emissions_factor = 0.428 * 4.536e4 * 1e-3 # (mTCO2/MWh) x (lb / mT) * (1 MWh / 10^3 kWh) = lb CO2 / kWh

    activity_usage_kwh = {
        "Charge an EV": 50, # based on 50 kwh battery on standard range plus model 3 tesla
        "Run a load of laundry": 5,
        "Take a hot shower": 8.2 # https://greengeekblog.com/tools/shower-cost-calculator/#:~:text=An%20average%208.2%20minute%20shower,energy%20to%20heat%20our%20water.
    }

    co2 = activity_usage_kwh[activity] * (nat_gas_mwh / total_supply * nat_gas_emissions_factor + \
        imports_mwh / total_supply * imports_emissions_factor)

    return co2 # lb

def generate_graph_forecasted():
    results = predict()
    fig3, ax3 = plt.subplots(figsize=(16,8))
    for source_type in results:
        lst = results[source_type].tolist()
        ax3.plot(range(len(lst)), lst)
    ax3.set_title('Forecasted Generation Mix for Next 24 hours')
    ax3.set_xlabel('Hours from Now')
    ax3.set_ylabel('MWh')
    ax3.legend(results.keys())

    return results, fig3

def generate_graph_historical_and_forecasted():
    genmix_vars = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas', 'Small hydro',
        'Coal', 'Nuclear', 'Batteries', 'Imports', 'Natural Gas',
        'Large Hydro']

    renewable = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas','Small hydro', 'Large Hydro', 'Nuclear']
    fossil_fuel = ['Coal', 'Natural Gas']   
    other = ['Batteries', 'Imports', 'Other']

    colors_grouped = ['#1f77b4','#ff7f0e','#2ca02c']
    colors_detailed = ['green','gray','brown','purple','orange','red','yellow','black','blue','pink','teal','lawngreen','indigo']

    """
    Plotting most recent CAISO data, grouped
    """

    # Get most recent CAISO data, then filter for today only
    data2 = get_last_n_days(1)
    length_today_only = int(60/5 * datetime.now(timezone('US/Pacific')).hour)
    data2 = data2.tail(length_today_only)

    # Add grouped columns
    data2['fossil_fuel'] = data2[fossil_fuel].sum(axis=1)
    data2['renewable'] = data2[renewable].sum(axis=1)
    data2['other'] = data2[other].sum(axis=1)

    # Set up grouped plot (ax2)
    fig2, ax2 = plt.subplots(figsize=(16,8))
    for source_indx, source in enumerate(['fossil_fuel','renewable','other']):
        ax2.plot(data2['date_time_5min'], data2[source], c=colors_grouped[source_indx])
    ax2.legend(['fossil_fuel','renewable','other'])

    # Set up detailed plot (ax3)
    fig3, ax3 = plt.subplots(figsize=(16,8))
    for source_indx, source in enumerate(genmix_vars):
        ax3.plot(data2['date_time_5min'], data2[source], c=colors_detailed[source_indx])
    ax3.legend(genmix_vars,loc='right')

    # Add the forecasting results
    results = predict() # local call

    # res = requests.get(f"https://sparc-cloud-run-hdyvu4kycq-uw.a.run.app/predict")
    # print('\n\n\nresult of call: ', res.text, '\n\n\n')
    # res = json.loads(res.text)['result']
    # results = {grouped_source: list(res[grouped_source].values()) for grouped_source in res.keys()}
    
    hours_from_pred = []
    for i in range(24):
        hours_from_pred.append(data2.iloc[-1]['date_time_5min'] + timedelta(hours=i))
    results['time'] = hours_from_pred

    for source_type in ['fossil_fuel','renewable','other']:
        lst = results[source_type].tolist() # need if calling locally
        # lst = results[source_type]
        ax2.plot(results['time'], lst)
        ax3.plot(results['time'], lst)

        # Add a vertical line
    for ax in ([ax2, ax3]):
        ax.vlines(x=data2.iloc[-1]['date_time_5min'], ymin=0,ymax=20000,colors='red',linestyles='dotted')
        ax.set_xlabel('Time')
        ax.set_ylabel('MWh')
        ax.set_xticklabels(ax.get_xticks(), rotation = 45)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%h-%d %I:%M%p'))

    return results, fig2, fig3

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
