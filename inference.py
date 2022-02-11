from skforecast.ForecasterAutoreg import ForecasterAutoreg
from joblib import load

def predict():
    trained_model_fn = 'saved_models/skforecast1hr/fossil_fuel_forecaster1hr.py'
    forecaster_loaded = load(trained_model_fn)

    pred = forecaster_loaded.predict(steps=24)
    return pred