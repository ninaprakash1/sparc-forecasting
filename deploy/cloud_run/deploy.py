import os
import time
import pickle
import logging

from fastapi import FastAPI
# from transformers import pipeline
from pydantic import BaseModel, PositiveInt, constr

import ray
from ray import serve

app = FastAPI()


logging.getLogger("Ray")

MODEL_NAME = "model.sav"


class Request(BaseModel):
    info: str
    data: dict


@serve.deployment
@serve.ingress(app)
class Model:
    def __init__(self):
        self.model = pickle.load(open(MODEL_NAME, 'rb'))

    @app.post("/")
    def predict(self, payload: Request):
        feature_vec = payload.data
        logging.info(f"Recieved data: {feature_vec}")
        preds = self.model.predict(1)
        return preds

ray.init(_node_ip_address="0.0.0.0") # needed for gcloud container compatibility
serve.start(
    http_options={"host": "0.0.0.0", "port": int(os.environ.get("PORT", "8000"))}
)
Model.deploy()

# Block the container process from exit
while True:
    time.sleep(5)
