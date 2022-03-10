# SPARC (Schedule Power and Reduce Carbon)

CS 329s @ Stanford University | Winter 2022

Team Members: Nina Prakash, Kun Guo, Griffin Tarpenning

SPARC is a web application that allows you to get the CO<sub>2</sub> emissions of daily activities at different durations and times of day by forecasting day-ahead generation mix.

### Datasets:

Energy data is from the California Independent System Operator (CAISO) and weather data is from World Weather Online (WWO).

### Modeling:

This is a time series forecasting problem where at every hour the features comprise the generation mix in MW per resource (solar, wind, geothermal, biomass, biogas, hydro, nuclear, batteries, imports, and other) and weather data (temperature, UV index, wind speed, cloud cover, humidity, and precipitation).

The output is the forecasted generation mix 24-hours ahead of time. We train 7 Skforecast models on aggregated energy source features (solar, wind, other_renewable (geothermal, biomass, biogas, and nuclear), hydro (small hydro and large hydro), batteries, and other (imports and other)) with an XGBoost regressor optimizing for MAPE.

The forecasted generation mix is then used to compute CO<sub>2</sub> emissions by using the carbon intensity of each source. The model only accounts for use-phase emissions.

### Backend: 

`cloudbuild.yaml` stores the Google Cloud Run configuration, building from `deploy/backend/Dockerfile`

`deploy/backend/` contains the backend code for the server, FastAPI endpoints, model loading, external endpoint hitting, etc.

### Other Infra

There are two branch-registered cloud triggers for deployments: 
1. Streamlit cloud on the `main` branch: pushes to main are deployed to frontend
2. Google Cloud Build Trigger: pushes to `deploy` trigger builds and deployment of backend

Additionally, a cron-job scheduler initiates an hourly retrain step, which was set up using the Google Console 

### Frontend

`frontend.py` contains the majority of the Streamlit code, calling `utils.py` when necessary. The frontend is publicly hosted at https://share.streamlit.io/ninaprakash1/sparc-forecasting/main/frontend.py.