from skforecast.ForecasterAutoreg import ForecasterAutoreg
import xgboost as xgb
import numpy as np
from joblib import dump

from utils import get_last_n_days

def train():
	last_2_years = get_last_n_days(365 * 2)

	# TODO @ Kun
	train_fossil_fuel_model(last_2_years)
	train_renewable_model(last_2_years)
	train_other_model(last_2_years)

def train_fossil_fuel_model(last_2_years):
    """
	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
	
	Train model on ['Coal','Natural Gas'] columns of last_2_years,
	with weather_vars ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
	as exog variable.

	Save model parameters as .py file to ./skforecast1hr/fossil_fuel_forecaster1hr.py
	"""
    ff_sc = ['Coal','Natural Gas']
    last_2_years['fossil_fuel'] = last_2_years[ff_sc].sum(axis=1)
    random_seed = 123
    regressor_f = xgb.XGBRegressor(random_state = random_seed, n_estimators = 1000,
                             gamma = 5, learning_rate = 0.01, max_depth = 3,
                             reg_lambda = 10, objective = 'reg:squarederror')
    forecaster_f = ForecasterAutoreg(
                    regressor = regressor_f,
                    lags      = np.arange(1, 25)
                )
    forecaster_f.fit(y = train['fossil_fuel'])

    dump(forecaster_f, './skforecast1hr/fossil_fuel_forecaster1hr.py')

def train_renewable_model(last_2_years):
    """
	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
	
	Train model on ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas','Small hydro', 'Large Hydro', 'Nuclear']
	columns of last_2_years, with weather_vars ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
	as exog variable.

	Save model parameters to ./skforecast1hr/renewable_forecaster1hr.py
	"""
    renewable_sc = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas','Small hydro', 'Large Hydro', 'Nuclear']
    last_2_years['renewable'] = last_2_years[renewable_sc].sum(axis=1)
    random_seed = 123
    regressor_r = xgb.XGBRegressor(random_state = random_seed, n_estimators = 1000,
                             gamma = 5, learning_rate = 0.01, max_depth = 5,
                             reg_lambda = 1, objective = 'reg:squarederror')
    forecaster_r = ForecasterAutoreg(
                regressor = regressor_r,
                lags      = np.arange(1, 25)
             )
    forecaster_r.fit(y = train['renewable'])

    dump(forecaster_r, './skforecast1hr/renewable_forecaster1hr.py')

def train_other_model(last_2_years):
    """
	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
	
	Train model on ['Batteries', 'Imports', 'Other'] columns of last_2_years, with weather_vars
	["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"] as exog variable.

	Save model parameters to ./skforecast1hr/other_forecaster1hr.py
	"""
    other_sc = ['Batteries', 'Imports', 'Other']
    last_2_years['other'] = last_2_years[other_sc].sum(axis=1)
    random_seed = 123
    regressor_o = xgb.XGBRegressor(random_state = random_seed, n_estimators = 1000,
                             gamma = 5, learning_rate = 0.01, max_depth = 5,
                             reg_lambda = 1, objective = 'reg:squarederror')
    forecaster_o = ForecasterAutoreg(
                regressor = regressor_o,
                lags      = np.arange(1, 25)
             )
    forecaster_o.fit(y = train['other'])

    dump(forecaster_o, './skforecast1hr/other_forecaster1hr.py')