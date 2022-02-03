# Use Python39
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set the WORKDIR to be the folder
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy requirements.txt to the docker image and install packages
ADD requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . ./


# Expose port 5000
EXPOSE 5000
ENV PORT 5000

# Use gunicorn as the entrypoint
CMD exec gunicorn --bind :$PORT main:app --workers 1 --threads 1 --timeout 60

# Local
# ENV FLASK_APP=main.py
# CMD ["flask", "run", "--host", "0.0.0.0"]
