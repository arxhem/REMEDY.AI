import folium
from folium.plugins import MarkerCluster, MiniMap

# User location data
user_location = {'latitude': 12.9716, 'longitude': 77.5946, 'name': 'User Location'}

# Doctors data
doctor_locations = [
    {'latitude': 12.975, 'longitude': 77.605, 'name': 'Doctor A', 'details': 'Cardiologist'},
    {'latitude': 12.982, 'longitude': 77.590, 'name': 'Doctor B', 'details': 'Dentist'},
    # Add more doctors here...
]

# Initialize the map with a light mode tile
m = folium.Map(location=[user_location['latitude'], user_location['longitude']], zoom_start=13, tiles='OpenStreetMap')

# Add user marker with a popup and a tooltip
folium.Marker(
    location=[user_location['latitude'], user_location['longitude']],
    popup=folium.Popup(f"<b>{user_location['name']}</b>", max_width=300),
    tooltip='User Location',
    icon=folium.Icon(color='blue', icon='user', prefix='fa')
).add_to(m)

# Initialize marker cluster for doctors
marker_cluster = MarkerCluster().add_to(m)

# Add doctor markers to the marker cluster with popups and tooltips
for doctor in doctor_locations:
    folium.Marker(
        location=[doctor['latitude'], doctor['longitude']],
        popup=folium.Popup(f"<b>{doctor['name']}</b><br>{doctor['details']}", max_width=300),
        tooltip=doctor['name'],
        icon=folium.Icon(color='red', icon='plus-square', prefix='fa')
    ).add_to(marker_cluster)
    
    # Draw line from user to doctor
    folium.PolyLine(
        locations=[
            [user_location['latitude'], user_location['longitude']],
            [doctor['latitude'], doctor['longitude']]
        ],
        color='green',
        weight=5
    ).add_to(m)

# Add a mini-map for better navigation
mini_map = MiniMap(toggle_display=True)
m.add_child(mini_map)

# Save the map to an HTML file
m.save('interactive_map.html')

# To display in a Jupyter notebook
m
