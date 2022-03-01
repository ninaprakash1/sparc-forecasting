import logging
from skforecast.ForecasterAutoreg import ForecasterAutoreg
import pandas as pd
from joblib import load
from utils import get_last_n_days


def predict(num_days=30):
	logging.info("Logging prediction hit")

	# Load models - check train.py for aggregated columns
	forecaster_battery = load("./skforecast1hr/Batteries_forecaster1hr.py")
	forecaster_ff = load("./skforecast1hr/fossil_fuel_forecaster1hr.py")
	forecaster_Hydro = load("./skforecast1hr/Hydro_forecaster1hr.py")
	forecaster_other = load("./skforecast1hr/other_forecaster1hr.py")
	forecaster_renewable = load("./skforecast1hr/renewable_forecaster1hr.py")
	forecaster_renewable_o = load("./skforecast1hr/renewable_other_forecaster1hr.py")
	forecaster_solar = load("./skforecast1hr/Solar_forecaster1hr.py")

	# Load train data
	weather_vars = ["tempC","uvIndex","WindGustKmph","cloudcover","humidity","precipMM"]

	# data = get_last_n_days(num_days)

	pred_battery = forecaster_battery.predict(steps = 24)
	pred_ff = forecaster_ff.predict(steps=24)
	pred_hydro = forecaster_Hydro.predict(steps = 24)
	pred_other = forecaster_other.predict(steps=24)
	pred_renewable = forecaster_renewable.predict(steps=24)
	pred_renewable_o = forecaster_renewable_o.predict(steps = 24)
	pred_solar = forecaster_solar.predict(steps = 24)

	pred_wind = pred_renewable - pred_renewable_o - pred_solar

	return {'battery':pred_battery, 'fossil_fuel': pred_ff, 'hydro': pred_hydro, 'other': pred_other,
			'renewable_other': pred_renewable_o, 'solar': pred_solar, 'wind': pred_wind
			}
