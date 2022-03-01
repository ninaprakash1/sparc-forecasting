from skforecast.ForecasterAutoreg import ForecasterAutoreg
import xgboost as xgb
import numpy as np
from joblib import dump
import logging

from utils import get_last_n_days

# all sources
energy = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas', 'Small hydro',
       'Coal', 'Nuclear', 'Batteries', 'Imports', 'Other', 'Natural Gas',
       'Large Hydro']

renewable = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas','Small hydro', 'Large Hydro', 'Nuclear']
fossil_fuel = ['Coal','Natural Gas']
other = ['Imports', 'Other']
hydro = ['Small hydro', 'Large Hydro']
renewable_other = ['Geothermal', 'Biomass', 'Biogas', 'Nuclear']

feat_cols = ['Hydro', 'Fossil_Fuel', 'Other', 'Renewable', 'Solar', 'Renewable_other']

def smooth_5min_data(data, kernel_size = 12):
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(data, kernel, mode='same')

def train(num_days=60):
    df_train = get_last_n_days(num_days)

    # aggregate energy sources
    df_train['Hydro'] = df_train[hydro].sum(axis =1)
    df_train['Fossil_Fuel'] = df_train[fossil_fuel].sum(axis =1)
    df_train['Other'] = df_train[other].sum(axis=1)
    df_train['Renewable'] = df_train[renewable].sum(axis =1)
    df_train['Renewable_other'] = df_train[renewable_other].sum(axis =1)

    dfs_train = df_train.copy()
    # smooth and resample 5min data to 1hr
    if len(df_train) > int(num_days)*48:
        kernel_size = 12
        for ycol in energy:
            dfs_train[ycol] = smooth_5min_data(df_train[ycol], kernel_size=kernel_size)
            dfs_train = dfs_train.iloc[::kernel_size, :]

    for feat_col in feat_cols:
        regressor = xgb.XGBRegressor(random_state=42, n_estimators=1000,
                                     gamma=10, learning_rate=0.01, max_depth=3,
                                     reg_lambda=10, objective='reg:squarederror')

        forecaster = ForecasterAutoreg(regressor=regressor, lags=24)

        forecaster.fit(y=dfs_train[feat_col])

        # Save model
        dump(forecaster, filename= './skforecast1hr/'+ feat_col +'_forecaster1hr.py')


# def train_fossil_fuel_model(last_2_years):
#     """
# 	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
#
# 	Train model on ['Coal','Natural Gas'] columns of last_2_years,
# 	with weather_vars ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
# 	as exog variable.
#
# 	Save model parameters as .py file to ./skforecast1hr/fossil_fuel_forecaster1hr.py
# 	"""
#     logging.info("Training Fossil model. ")
#
#     ff_sc = ['Coal','Natural Gas']
#     weather_vars = ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
#     last_2_years['fossil_fuel'] = last_2_years[ff_sc].sum(axis=1)
#     random_seed = 123
#     regressor_f = xgb.XGBRegressor(random_state = random_seed, n_estimators = 1000,
#                              gamma = 5, learning_rate = 0.01, max_depth = 3,
#                              reg_lambda = 10, objective = 'reg:squarederror')
#     forecaster_f = ForecasterAutoreg(
#                     regressor = regressor_f,
#                     lags      = np.arange(1, 25)
#                 )
#     forecaster_f.fit(y = last_2_years['fossil_fuel'], exog = last_2_years[weather_vars])
#
#     dump(forecaster_f, './skforecast1hr/fossil_fuel_forecaster1hr.py')
#
#
# def train_renewable_model(last_2_years):
#     """
# 	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
#
# 	Train model on ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas','Small hydro', 'Large Hydro', 'Nuclear']
# 	columns of last_2_years, with weather_vars ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
# 	as exog variable.
#
# 	Save model parameters to ./skforecast1hr/renewable_forecaster1hr.py
# 	"""
#     logging.info("Training Renewable model. ")
#     weather_vars = ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
#     renewable_sc = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas','Small hydro', 'Large Hydro', 'Nuclear']
#     last_2_years['renewable'] = last_2_years[renewable_sc].sum(axis=1)
#     random_seed = 123
#     regressor_r = xgb.XGBRegressor(random_state = random_seed, n_estimators = 1000,
#                              gamma = 5, learning_rate = 0.01, max_depth = 5,
#                              reg_lambda = 1, objective = 'reg:squarederror')
#     forecaster_r = ForecasterAutoreg(
#                 regressor = regressor_r,
#                 lags      = np.arange(1, 25)
#              )
#     forecaster_r.fit(y = last_2_years['renewable'], exog = last_2_years[weather_vars])
#
#     dump(forecaster_r, './skforecast1hr/renewable_forecaster1hr.py')
#
#
# def train_other_model(last_2_years):
#     """
# 	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
#
# 	Train model on ['Batteries', 'Imports', 'Other'] columns of last_2_years, with weather_vars
# 	["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"] as exog variable.
#
# 	Save model parameters to ./skforecast1hr/other_forecaster1hr.py
# 	"""
#     logging.info("Training OTHER model. ")
#
#     other_sc = ['Batteries', 'Imports', 'Other']
#     weather_vars = ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
#     last_2_years['other'] = last_2_years[other_sc].sum(axis=1)
#     random_seed = 123
#     regressor_o = xgb.XGBRegressor(random_state = random_seed, n_estimators = 1000,
#                              gamma = 5, learning_rate = 0.01, max_depth = 5,
#                              reg_lambda = 1, objective = 'reg:squarederror')
#     forecaster_o = ForecasterAutoreg(
#                 regressor = regressor_o,
#                 lags      = np.arange(1, 25)
#              )
#     forecaster_o.fit(y = last_2_years['other'], exog = last_2_years[weather_vars])
#
#     dump(forecaster_o, './skforecast1hr/other_forecaster1hr.py')
