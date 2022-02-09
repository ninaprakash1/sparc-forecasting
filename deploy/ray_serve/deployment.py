import os
import tempfile
import json 
import pickle

from fastapi import FastAPI
import ray
from ray import serve

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


# app = FastAPI()
# ray.init(address='10.138.0.2:6379', _redis_password='5241590000000000')  # address="auto", 

ray.init(address="auto", namespace="regressor")  #
client = serve.start(
    detached=True,
    # http_options={"http_middlewares": [Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'])]}
)


# Save the model and label to file
MODEL_PATH = os.path.join(tempfile.gettempdir(),
                          "iris_model_logistic_regression.pkl")
LABEL_PATH = os.path.join(tempfile.gettempdir(), "iris_labels.json")


@serve.deployment(route_prefix="/api")
# @serve.ingress(app)
class BoostingModel:
    def __init__(self):
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)
        with open(LABEL_PATH) as f:
            self.label_list = json.load(f)

    async def __call__(self, starlette_request):
        payload = await starlette_request.json()
        print("Worker: received data", payload)

        input_vector = [
            payload["sepal length"],
            payload["sepal width"],
            payload["petal length"],
            payload["petal width"],
        ]
        prediction = self.model.predict([input_vector])[0]
        human_name = self.label_list[prediction]
        return {"result": human_name}

BoostingModel.deploy()


import requests

sample_request_input = {
    "sepal length": 1.2,
    "sepal width": 1.0,
    "petal length": 1.1,
    "petal width": 0.9
}

r = requests.get('http://0.0.0.0:8000/api', json=sample_request_input)
print(f"REQUEST 2: {r.text}")