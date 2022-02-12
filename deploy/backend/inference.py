import logging
from skforecast.ForecasterAutoreg import ForecasterAutoreg
import pandas as pd
from joblib import load


def predict():
	logging.info("Logging prediction hit")

	# Load model
	forecaster_loaded = load("saved_models/skforecast1hr/fossil_fuel_forecaster1hr.py")

	# Load train data
	train_x_fn = "data/X_train_california_2020-2021.csv"
	weather_vars = ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
	data = pd.read_csv(train_x_fn)
	
	pred_ff = forecaster_loaded.predict(steps=24, exog = data[weather_vars])

	# return 'Not implemented'
	return pred_ff
