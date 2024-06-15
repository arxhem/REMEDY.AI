import requests

# Replace with your actual address and API key
address = "Impressions Dental Specialities, Number 864, Prakriti, D Block, 60 Feet Road, Landmark: Above Third Wave Coffee, Bangalore"
api_key = "AIzaSyAX5ZS6FZ2Da911ijwDjEFllxjEbRCtN5c"

# Construct the URL
url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(address)}&key={api_key}"

# Send the GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        location = data['results'][0]['geometry']['location']
        print(f"Latitude: {location['lat']}, Longitude: {location['lng']}")
    else:
        print("No results found")
else:
    print(f"Error: {response.status_code}, {response.text}")
