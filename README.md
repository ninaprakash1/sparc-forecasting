# cs329s-project

Forecasting the CO<sub>2</sub> emissions of daily activities.

### Backend: 

`cloudbuild.yaml` stores the Google Cloud Run configuration, building from `deploy/backend/Dockerfile`

`deploy/backend/` contains the backend code for the server, FastAPI endpoints, model loading, external endpoint hitting, etc.

### Other Infra

There are two branch-registered cloud triggers for deployments: 
1. Streamlit cloud on the `main` branch: pushes to main are deployed to frontend
2. Google Cloud Build Trigger: pushes to `deploy` trigger builds and deployment of backend

Additionally, a cron-job scheduler initiates an hourly retrain step, which was set up using the Google Console 

### Frontend

`frontend.py` contains the majority of the Streamlit code, calling `utils.py` when necessary



### Resources

1. [Overleaf](https://www.overleaf.com/project/61e08b364ca87fbbf9d59f3a)
2. [Existing scrapers from tamu](https://github.com/tamu-engineering-research/COVID-EMDA/tree/master/parser)
3. [World Weather Online](https://www.worldweatheronline.com/developer/)
