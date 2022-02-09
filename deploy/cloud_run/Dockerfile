FROM rayproject/ray:1.10.0
EXPOSE 8000

# pip dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# runtime
COPY . .
CMD bash -c "python deploy.py"
