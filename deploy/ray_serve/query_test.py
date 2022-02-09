import requests

sample_request_input = {
    "sepal length": 1.2,
    "sepal width": 1.0,
    "petal length": 1.1,
    "petal width": 0.9
}

r = requests.get('http://0.0.0.0:8000/api', json=sample_request_input)
print(f"REQUEST: {r.text}")