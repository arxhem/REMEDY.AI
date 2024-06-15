import pandas as pd
from keplergl import KeplerGl

# User location data
user_data = {
    'latitude': [12.9716],
    'longitude': [77.5946],
    'name': ['User Location']
}

# Doctors data
doctors_data = [
    {'latitude': 12.975, 'longitude': 77.605, 'name': 'Doctor A', 'details': 'Cardiologist'},
    {'latitude': 12.982, 'longitude': 77.590, 'name': 'Doctor B', 'details': 'Dentist'},
    # Add more doctors here...
]

# Connections data
connections_data = []
for doctor in doctors_data:
    connections_data.append({
        'start_lat': user_data['latitude'][0],
        'start_lng': user_data['longitude'][0],
        'end_lat': doctor['latitude'],
        'end_lng': doctor['longitude'],
        'name': doctor['name'],
        'details': doctor['details']
    })

# Convert to DataFrame
user_df = pd.DataFrame(user_data)
doctors_df = pd.DataFrame(doctors_data)
connections_df = pd.DataFrame(connections_data)

# Initialize Kepler.gl map
map_ = KeplerGl(height=600)

# Add data to the map
map_.add_data(data=user_df, name="User Location")
map_.add_data(data=doctors_df, name="Doctors")
map_.add_data(data=connections_df, name="Connections")

# Configure Kepler.gl map
config = {
    'version': 'v1',
    'config': {
        'visState': {
            'layers': [
                {
                    'id': 'user_layer',
                    'type': 'point',
                    'config': {
                        'dataId': 'User Location',
                        'label': 'User Location',
                        'color': [30, 144, 255],
                        'columns': {
                            'lat': 'latitude',
                            'lng': 'longitude',
                            'altitude': None
                        },
                        'isVisible': True,
                        'visConfig': {
                            'radius': 15,  # Increased radius for larger dots
                            'colorRange': {
                                'name': 'Custom Palette',
                                'type': 'custom',
                                'category': 'Custom',
                                'colors': ['#1f77b4']
                            },
                            'filled': True
                        }
                    }
                },
                {
                    'id': 'doctors_layer',
                    'type': 'point',
                    'config': {
                        'dataId': 'Doctors',
                        'label': 'Doctors',
                        'color': [255, 0, 0],
                        'columns': {
                            'lat': 'latitude',
                            'lng': 'longitude',
                            'altitude': None
                        },
                        'isVisible': True,
                        'visConfig': {
                            'radius': 15,  # Increased radius for larger dots
                            'colorRange': {
                                'name': 'Custom Palette',
                                'type': 'custom',
                                'category': 'Custom',
                                'colors': ['#ff0000']
                            },
                            'filled': True
                        }
                    }
                },
                {
                    'id': 'connections_layer',
                    'type': 'line',
                    'config': {
                        'dataId': 'Connections',
                        'label': 'Connections',
                        'color': [0, 255, 0],
                        'columns': {
                            'lat0': 'start_lat',
                            'lng0': 'start_lng',
                            'lat1': 'end_lat',
                            'lng1': 'end_lng'
                        },
                        'isVisible': True,
                        'visConfig': {
                            'opacity': 0.8,
                            'thickness': 2,
                            'colorRange': {
                                'name': 'Custom Palette',
                                'type': 'custom',
                                'category': 'Custom',
                                'colors': ['#00ff00']
                            }
                        }
                    }
                }
            ]
        },
        'mapState': {
            'bearing': 0,
            'dragRotate': True,
            'latitude': 12.978,  # Center latitude to better fit all points
            'longitude': 77.597,  # Center longitude to better fit all points
            'pitch': 0,
            'zoom': 14,  # Set an initial zoom level to fit the map nicely
            'isSplit': False
        },
        'mapStyle': {
            'styleType': 'dark',
            'topLayerGroups': {},
            'visibleLayerGroups': {
                'label': True,
                'road': True,
                'border': False,
                'building': True,
                'water': True,
                'land': True,
                '3d building': False
            },
            'threeDBuildingColor': [9.665468314072013, 17.18305478057247, 31.1442867897876],
            'mapStyles': {}
        }
    }
}

# Apply configuration
map_.config = config

# Save the map as an HTML file
map_.save_to_html(file_name='kepler_map.html')

# To display in a Jupyter notebook, you can use
# map_
