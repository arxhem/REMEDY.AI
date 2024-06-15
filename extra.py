
import folium
from folium.plugins import MarkerCluster, MiniMap
import json 
import requests

def get_coordinates(address, api_key):
    # Construct the URL for the Geocoding API
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address=requests.utils.quote(address)&key=api_key"

    # Send the GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"No results found for address: address")
            return None
    else:
        print(f"Error: response.status_code, response.text")
        return None

# User location data
user_location = {'latitude': 12.9716, 'longitude': 77.5946, 'name': 'User Location'}

def extract_addresses_from_json(file_path):
    addresses = []
    with open(file_path, 'r') as file:
        data = json.load(file)
        for entry in data:
            if 'address' in entry and 'doctor_name' in entry:
                addresses.append((entry['address'], entry['doctor_name']))
    return addresses

def create_map(addresses, api_key):
    # Initialize the map with a light mode tile
    m = folium.Map(location=[user_location['latitude'], user_location['longitude']], zoom_start=13, tiles='OpenStreetMap')

    # Add user marker with a popup and a tooltip
    folium.Marker(
        location=[user_location['latitude'], user_location['longitude']],
        popup=folium.Popup(f"<b>user_location['name']</b>", max_width=300),
        tooltip='User Location',
        icon=folium.Icon(color='blue', icon='user', prefix='fa')
    ).add_to(m)

    # Initialize marker cluster for doctors
    marker_cluster = MarkerCluster().add_to(m)

    # Iterate through each address
    for address, doctor_name in addresses:
        coordinates = get_coordinates(address, api_key)
        if coordinates:
            latitude, longitude = coordinates
            folium.Marker(
                location=[latitude, longitude],
                popup=folium.Popup(f"<b>doctor_name</b>", max_width=300),
                tooltip=doctor_name,
                icon=folium.Icon(color='red', icon='plus-square', prefix='fa')
            ).add_to(marker_cluster)

            # Draw line from user to doctor
            folium.PolyLine(
                locations=[
                    [user_location['latitude'], user_location['longitude']],
                    [latitude, longitude]
                ],
                color='green',
                weight=1
            ).add_to(m)

    # Add a mini-map for better navigation
    mini_map = MiniMap(toggle_display=True)
    m.add_child(mini_map)

    # Return the map object
    return m

if __name__ == "__main__":
    # Replace with your actual addresses and API key
    addresses = extract_addresses_from_json('dictionaries.json')
    
    api_key = "AIzaSyAX5ZS6FZ2Da911ijwDjEFllxjEbRCtN5c"

    # Create a map with the given addresses
    my_map = create_map(addresses, api_key)

    # Save the map to an HTML file
    my_map.save('interactive_map.html')
    
    print(f"Map has been saved to interactive_map.html")