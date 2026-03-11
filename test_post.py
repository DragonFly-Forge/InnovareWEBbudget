import requests

url = 'http://127.0.0.1:5000/api/add-transaction'
data = {
    "user_id": 1,
    "category_id": 1,
    "amount": 50.0,
    "description": "Tea at IEM canteen"
}

response = requests.post(url, json=data)
print(response.json())