import uuid

import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np
import logging

from inference import predict
from train import train
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
    num_days = 30
    logging.info(f",,{param_str.count('days=')}")
    if param_str.count("days=") == 1:
        num_days = int(param_str.split("days=")[1].strip())
        logging.info("retraining with n={num_days}")
    else:
        return {"result": "Enter correct days param"}

    try: 
        train(num_days)

        logging.info(f"Renewable test: {test_model('./skforecast1hr/renewable_forecaster1hr.py')}")
        logging.info(f"Fossil test: {test_model('./skforecast1hr/fossil_fuel_forecaster1hr.py')}")
        logging.info(f"Other test: {test_model('./skforecast1hr/other_forecaster1hr.py')}")
        
        return {"result": f"Retrain Successful!"}
    except Exception as e:
        logging.warning(e)
        return {"result": f"{e}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)

    