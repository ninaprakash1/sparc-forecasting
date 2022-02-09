import ray

from fastapi import FastAPI
from ray import serve


app = FastAPI()
ray.init(address='10.138.0.2:6379', _redis_password='5241590000000000')  # address="auto", 
serve.start(detached=True)

@serve.deployment(route_prefix="/api")
@serve.ingress(app)
class MyFastAPIDeployment:
    def __init__(self):
      self.count = 0

    @app.get("/")
    def get(self):
        return {"count": self.count}

    @app.get("/predict")
    def incr(self):
        self.count += 1
        return {"count": self.count}

    @app.get("/decr")
    def decr(self):
        self.count -= 1
        return {"count": self.count}

MyFastAPIDeployment.deploy()