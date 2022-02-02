#!/bin/bash

gcloud auth configure-docker
docker build -t cloud-runner .
