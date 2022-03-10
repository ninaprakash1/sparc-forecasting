from skforecast.ForecasterAutoreg import ForecasterAutoreg
import xgboost as xgb
import numpy as np
from joblib import dump
import logging
import os

from utils import get_last_n_days

energy_map = {
    "Renewable": [
        "Solar",
        "Wind",
        "Geothermal",
        "Biomass",
        "Biogas",
        "Small hydro",
        "Large Hydro",
        "Nuclear",
    ],
    "Fossil_fuel": ["Coal", "Natural Gas"],
    "Other": ["Imports", "Other"],
    "Hydro": ["Small hydro", "Large Hydro"],
    "Renewable_other": ["Geothermal", "Biomass", "Biogas", "Nuclear"],
    "Solar": ["Solar"],
    "Batteries": ["Batteries"],
    "Total": [
        "Solar",
        "Wind",
        "Geothermal",
        "Biomass",
        "Biogas",
        "Small hydro",
        "Coal",
        "Nuclear",
        "Batteries",
        "Imports",
        "Other",
        "Natural Gas",
        "Large Hydro",
    ],
}


def smooth_5min_data(data, kernel_size=12):
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(data, kernel, mode="same")


def train(num_days=30):
    df_train = get_last_n_days(num_days)

    dfs_train = df_train.copy()
    # smooth and resample 5min data to 1hr
    if len(df_train) > int(num_days) * 48:
        kernel_size = 12
        for ycol in energy_map["Total"]:
            dfs_train[ycol] = smooth_5min_data(df_train[ycol], kernel_size=kernel_size)

        dffs_train = dfs_train.iloc[::kernel_size, :]
    else:
        dffs_train = df_train.copy()

    for feat_col in energy_map:
        features = energy_map[feat_col]
        data = dffs_train[features].sum(axis=1)

        regressor = xgb.XGBRegressor(
            random_state=42,
            n_estimators=1000,
            gamma=10,
            learning_rate=0.01,
            max_depth=3,
            reg_lambda=10,
            objective="reg:squarederror",
        )
        forecaster = ForecasterAutoreg(regressor=regressor, lags=24)
        forecaster.fit(y=data)

        # Save model
        if "./skforecast1hr" not in os.listdir():
            os.mkdir("skforecast1hr")

        dump(forecaster, filename=f"./skforecast1hr/{feat_col}_forecaster1hr.py")

    logging.info(f"{['./skforecast1hr/' + x for x in os.listdir('./skforecast1hr')]}")
