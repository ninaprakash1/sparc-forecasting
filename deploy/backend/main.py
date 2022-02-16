import uuid

import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np
import logging

from inference import predict
from train import train_renewable_model, train_fossil_fuel_model, train_other_model
from utils import test_model


app = FastAPI()

""" Import Models """


""" Load Data """


""" Class Definition Here? (store models in state)"""
@app.get("/predict")
def get_prediction():
    return {"result": predict()}


@app.get("/")
def read_root():
    """ Root endpoint, TODO: display basic info (readme?) """
    return {"message": "Welcome from the API"}


""" Example query param request """
@app.get("/train/{param_str}")
def train_models(param_str: str):
    """ Experimental endpoint to retrain models, accepts param str """
    logging.info(f"Recieved request for retrain with param_str: {param_str}")
    if "years=2" in param_str:
        logging.info("retraining with n=730")

    try: 
        train_renewable_model(730)
        logging.info(f"Renewable test: {test_model('renewable_forecaster1hr.py')}")

        train_fossil_fuel_model(730)
        logging.info(f"Fossil test: {test_model('fossil_fuel_forecaster1hr.py')}")

        train_other_model(730)
        logging.info(f"Other test: {test_model('other_forecaster1hr.py')}")
        
        return {"result": f"Retrain Successful!"}
    except Exception as e:
        return {"result": f"{e}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)

    