import uuid

import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np

from inference import predict


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


@app.get("/echo/{message}")
def read_root(message: str):
    return {"message": f"{message}"}

@app.get("/predict")
def get_prediction():
    return {"result": predict()}


@app.post("/{get_info}")
def get_image(get_info: str):
    return {"name": get_info}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
