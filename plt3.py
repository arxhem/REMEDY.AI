import plotly.graph_objects as go

# Coordinates
user_lat, user_lng = 12.9716, 77.5946  # Example coordinates for Bangalore
doctor_coords = [
    {'name': 'Doctor A', 'lat': 12.975, 'lng': 77.605, 'details': 'Cardiologist'},
    {'name': 'Doctor B', 'lat': 12.982, 'lng': 77.590, 'details': 'Dentist'},
    # Add more doctors here...
]

# Mapbox access token
mapbox_access_token = ""

# Create scatter mapbox trace for user
user_trace = go.Scattermapbox(
    lat=[user_lat],
    lon=[user_lng],
    mode='markers+text',
    marker=dict(size=14, color='blue'),
    text=["User Location"],
    textposition='top center'
)

# Create scatter mapbox traces for doctors and connections
doctor_traces = []
lines = []

for doctor in doctor_coords:
    doctor_traces.append(
        go.Scattermapbox(
            lat=[doctor['lat']],
            lon=[doctor['lng']],
            mode='markers+text',
            marker=dict(size=10, color='red'),
            text=[f"{doctor['name']}, {doctor['details']}"],
            textposition='top right'
        )
    )
    lines.append(
        go.Scattermapbox(
            lat=[user_lat, doctor['lat']],
            lon=[user_lng, doctor['lng']],
            mode='lines',
            line=dict(width=2, color='green')
        )
    )

# Create the figure
fig = go.Figure()

# Add all traces to the figure
fig.add_trace(user_trace)
for trace in doctor_traces:
    fig.add_trace(trace)
for line in lines:
    fig.add_trace(line)

# Update layout for mapbox
fig.update_layout(
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style='mapbox://styles/mapbox/streets-v11',  # You can change the style here
        center=dict(lat=user_lat, lon=user_lng),
        zoom=13
    ),
    margin=dict(l=0, r=0, t=0, b=0)
)

# Show the map
fig.show()
