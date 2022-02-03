"""
A sample flask application on Cloud Run.


https://medium.com/fullstackai/how-to-deploy-a-simple-flask-app-on-cloud-run-with-cloud-endpoint-e10088170eb7
"""

from flask import Flask, render_template
from flask_cors import CORS
from flask_sslify import SSLify

from webargs import fields
from webargs.flaskparser import use_args

import utils

import logging
import pickle
import json

# Initialise flask app
app = Flask(__name__)
# CORS(app, supports_credentials=True)
# sslify = SSLify(app)

MODEL_NAME = "model.pkl"


# Load Model (one time per deployment, no retrain)
model = pickle.load( open( MODEL_NAME, "rb" ) )
    

@app.route("/get_info/<other_data>", methods=["GET"])
def get_info(other_data):
    """ Return model version / other misc info """
    other_data = other_data or "No param passed"
    data = {
        "model_name": MODEL_NAME,
        "other_data": other_data,
    }
    return json.dumps(data), 200


# @app.route("/predict", methods=["POST"])
# @use_args(argmap={"params": fields.Str(required=False)})
# def predict(args):
#     """ Makes a prediction with optional arguments """
#     params   = args.get("params", "")
#     logging.info(f"got params: {params}")

#     weather  = utils.get_updated_weather_data()
#     mix      = utils.get_updated_mix_data()
#     features = weather.update(mix)
#     preds    = model.predict(features)

#     return json.dumps(preds), 200

@app.route("/predict", methods=["GET"])
def predict():
    """ Makes a prediction with optional arguments """
    # params   = args.get("params", "")
    # logging.info(f"got params: {params}")

    weather  = utils.get_updated_weather_data()
    mix      = utils.get_updated_mix_data()
    features = weather.update(mix)
    # preds    = model.predict(features)
    preds = {"fake_preds": [0 for i in range(10)]}

    return json.dumps(preds), 200


@app.route("/")
def index():
    """ Home Page HTML """
    return render_template("index.html")
    # return "asdas\n"


if __name__ == "__main__":
    app.run(ssl_context="adhoc", host="0.0.0.0", port=5000, debug=True)
