import ray
from ray import serve
from fastapi import FastAPI


ray.init()

serve.start()

@serve.deployment
@serve.ingress(app)
class Counter:
  def __init__(self):
      self.count = 0

  @app.get("/")
  def get(self):
      return {"count": self.count}

  @app.get("/incr")
  def incr(self):
      self.count += 1
      return {"count": self.count}

  @app.get("/decr")
  def decr(self):
      self.count -= 1
      return {"count": self.count}
