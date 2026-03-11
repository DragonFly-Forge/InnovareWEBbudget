import requests

# The URL for your new income route
url = 'http://127.0.0.1:5000/api/add-income'

# Data for the "Pocket Money" deposit
data = {
    "user_id": 1,
    "category_id": 7,  # Category 7 is 'Other' in your SQL seed
    "amount": 1000.0,
    "description": "Monthly Pocket Money"
}

try:
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)