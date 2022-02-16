from utils import get_last_n_days

def train():
	last_2_years = get_last_n_days(365 * 2)

	# TODO @ Kun
	train_fossil_fuel_model(last_2_years)
	train_renewable_model(last_2_years)
	train_other_model(last_2_years)

def train_fossil_fuel_model(last_2_years):
	# TODO @ Kun
	"""
	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
	
	Train model on ['Coal','Natural Gas'] columns of last_2_years,
	with weather_vars ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
	as exog variable.

	Save model parameters as .py file to ./skforecast1hr/fossil_fuel_forecaster1hr.py
	"""
	pass

def train_renewable_model(last_2_years):
	# TODO @ Kun
	"""
	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
	
	Train model on ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas','Small hydro', 'Large Hydro', 'Nuclear']
	columns of last_2_years, with weather_vars ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
	as exog variable.

	Save model parameters to ./skforecast1hr/renewable_forecaster1hr.py
	"""
	pass

def train_other_model(last_2_years):
	# TODO @ Kun
	"""
	@param		last_2_years		Dataframe with same columns as X_train_california_2020-2021.csv
	
	Train model on ['Batteries', 'Imports', 'Other'] columns of last_2_years, with weather_vars
	["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"] as exog variable.

	Save model parameters to ./skforecast1hr/other_forecaster1hr.py
	"""
	pass