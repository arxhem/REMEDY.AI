import requests

url = 'http://127.0.0.1:5000/get_doctors'
payload = {
    "specialization": "Dentist",
    "user": {
        "lat": 13.061055,
        "long": 77.587222
    },
    "location": "Bangalore"
}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
