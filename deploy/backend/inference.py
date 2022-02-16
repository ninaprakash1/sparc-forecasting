import logging
from skforecast.ForecasterAutoreg import ForecasterAutoreg
import pandas as pd
from joblib import load
from utils import get_last_n_days


def predict(num_days=5):
	logging.info("Logging prediction hit")

	# Load model
	forecaster_ff = load("./skforecast1hr/fossil_fuel_forecaster1hr.py")
	forecaster_renewable = load("./skforecast1hr/renewable_forecaster1hr.py")
	forecaster_other = load("./skforecast1hr/other_forecaster1hr.py")

	# Load train data
	train_x_fn = "./X_train_california_2020-2021.csv"
	weather_vars = ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]

	data = get_last_n_days(num_days)

	pred_ff = forecaster_ff.predict(steps=24, exog = data[weather_vars])
	pred_renewable = forecaster_renewable.predict(steps=24, exog = data[weather_vars])
	pred_other = forecaster_other.predict(steps=24, exog = data[weather_vars])

	return {'fossil_fuel': pred_ff, 'renewable': pred_renewable, 'other': pred_other}
