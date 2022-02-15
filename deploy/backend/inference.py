import logging
from skforecast.ForecasterAutoreg import ForecasterAutoreg
import pandas as pd
from joblib import load


def predict():
	logging.info("Logging prediction hit")
<<<<<<< HEAD

	# Load model
	forecaster_ff = load("saved_models/skforecast1hr/fossil_fuel_forecaster1hr.py")
	forecaster_renewable = load("saved_models/skforecast1hr/renewable_forecaster1hr.py")
	forecaster_other = load("saved_models/skforecast1hr/other_forecaster1hr.py")

	# Load train data
	train_x_fn = "data/X_train_california_2020-2021.csv"
	weather_vars = ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
	data = pd.read_csv(train_x_fn)
	
=======
	print("Logging prediction hit -- print statement")

	# Load model
	forecaster_ff = load("./skforecast1hr/fossil_fuel_forecaster1hr.py")
	forecaster_renewable = load("./skforecast1hr/renewable_forecaster1hr.py")
	forecaster_other = load("./skforecast1hr/other_forecaster1hr.py")

	print("Loaded models")	

	# Load train data
	train_x_fn = "X_train_california_2020-2021.csv"
	weather_vars = ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]
	data = pd.read_csv(train_x_fn)
	

	print("loaded training data")

>>>>>>> de8a3ea62c6ace99c4eea94737cb59a710e219dd
	pred_ff = forecaster_ff.predict(steps=24, exog = data[weather_vars])
	pred_renewable = forecaster_renewable.predict(steps=24, exog = data[weather_vars])
	pred_other = forecaster_other.predict(steps=24, exog = data[weather_vars])

<<<<<<< HEAD
	return {'fossil_fuel': pred_ff, 'renewable': pred_renewable, 'other': pred_other}
=======
	return {'fossil_fuel': pred_ff, 'renewable': pred_renewable, 'other': pred_other}
>>>>>>> de8a3ea62c6ace99c4eea94737cb59a710e219dd
