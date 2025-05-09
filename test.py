import requests

url = "http://localhost:8002/fold/"
data = {
    "sequences": ["TQVCTGTDMKLRLPASPETHLDMLRHLYQGCQVVQGNLELTYLP","TNASLSFLQDIQEVQGYVLIAHNQVRQVPLQRLRIVRG"],
}

response = requests.post(url, json=data)

print("Response:", response.json())
