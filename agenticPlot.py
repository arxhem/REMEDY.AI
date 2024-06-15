import json
import folium
import requests

# Load the JSON data
with open('dictionaries.json', 'r') as file:
    data = json.load(file)

# Extract addresses and names
doctor_addresses = []
doctor_names = []

for doctor in data:
    doctor_addresses.append(doctor['address'])
    doctor_names.append(doctor['doctor_name'])

# Google's Geolocation API key
api_key = "AIzaSyAX5ZS6FZ2Da911ijwDjEFllxjEbRCtN5c"

# Function to get latitude and longitude
def get_lat_long(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(address)}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json().get('results')
        if result:
            location = result[0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None

# Get user location (example coordinates, you can modify)
user_location = (13.0610556, 77.587222)  # San Francisco, CA

# Create a map centered at the user's location
mymap = folium.Map(location=user_location, zoom_start=13)

# Add a marker for the user location
folium.Marker(user_location, tooltip="User Location", icon=folium.Icon(color='blue')).add_to(mymap)

# Add markers for doctors and lines connecting to user location
for address, name in zip(doctor_addresses, doctor_names):
    lat, lng = get_lat_long(address)
    if lat is not None and lng is not None:
        folium.Marker([lat, lng], popup=name, tooltip=name, icon=folium.Icon(color='red')).add_to(mymap)
        folium.PolyLine([user_location, (lat, lng)], color='green').add_to(mymap)

# Save the map as an HTML file
mymap.save("doctors_map.html")