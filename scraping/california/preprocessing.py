import pandas as pd

# merge generation mix and weather data

# Load data files
genmix_data_file = "california_genmix_20200101_20211231.csv"
weather_data_file = "california_weather_20200101_20220119.csv"

genmix = pd.read_csv(genmix_data_file, dtype={'Day':str,'Time':str})
weather = pd.read_csv(weather_data_file).rename(columns={'date_time':'date_time_hourly'})

# Add datetime column to generation mix data
genmix['date_time_5min'] = genmix.Day + " " + genmix.Time
genmix.date_time_5min = pd.to_datetime(genmix.date_time_5min)
genmix['date_time_hourly'] = genmix.date_time_5min.dt.floor('h')
genmix = genmix[['date_time_hourly','date_time_5min','Solar','Wind','Geothermal','Biomass','Biogas','Small hydro','Coal','Nuclear','Batteries','Imports','Other','Natural Gas','Large Hydro']]

# Remove 2022 from weather data
weather.date_time_hourly = pd.to_datetime(weather.date_time_hourly)
weather = weather[weather.date_time_hourly < pd.to_datetime('20220101', format='%Y%m%d')]

# Define weather columns to keep
weather_cols = ['date_time_hourly','tempC', 'uvIndex','WindGustKmph','cloudcover','humidity','precipMM']
weather = weather[weather_cols]

# Join data by datetime
full_data = genmix.set_index('date_time_hourly').join(weather.set_index('date_time_hourly'),on='date_time_hourly')

# Reset timestamp to 5-min frequency
full_data.reset_index(drop=True, inplace=True)
full_data.to_csv('california_full_data_20200101_20211231.csv')