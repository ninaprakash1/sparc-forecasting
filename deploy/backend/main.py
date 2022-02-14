import uuid

import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np

from inference import predict


app = FastAPI()

""" Import Models """


""" Load Data """


""" Class Definition Here? (store models in state)"""
@app.get("/predict")
def get_prediction():
    return {"result": predict()}


# """ Sample Post Request """
# @app.post("/{get_info}")
# def get_image(get_info: str):
#     return {"name": get_info}

@app.get("/")
def read_root():
    """ Root endpoint, TODO: display basic info (readme?) """
    return {"message": "Welcome from the API"}


""" Example query param request """
# @app.get("/help/{message}")
# def read_root(message: str):
#     return {"message": f"{message}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
