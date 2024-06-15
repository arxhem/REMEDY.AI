import { useEffect, useState } from 'react';
let city="";
export const GeoLocationComponent = () => {
    const [locationData, setLocationData] = useState(null);
    const [error, setError] = useState(null);

    

    useEffect(() => {
        const getLocation = () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        let lat = position.coords.latitude;
                        let long = position.coords.longitude;
                        console.log("Latitude:", lat, "Longitude:", long);
                        getCountyFromCoordinates(lat, long);
                    },
                    (error) => {
                        handleGeolocationError(error);
                    },
                    {
                        timeout: 10000
                    }
                );
            } else {
                setError("Geolocation is not supported by this browser.");
            }
        };

        const getCountyFromCoordinates = (lat, long) => {
            
            // Replace this with your logic to fetch county details based on coordinates
            // For example, fetch from an API like Nominatim or OpenCage
            fetch("https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${long}")
                .then(response => response.json())
                .then(data => {
                    console.log("County:", data.address.county);
                    setLocationData({ latitude: lat, longitude: long, county: data.address.county });
                    city=data.address.county;
                })
                .catch(error => {
                    setError("Error fetching county information.");
                    console.error('Error:', error);
                });
                
        };

        const handleGeolocationError = (error) => {
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    setError("User denied the request for Geolocation.");
                    break;
                case error.POSITION_UNAVAILABLE:
                    setError("Location information is unavailable.");
                    break;
                case error.TIMEOUT:
                    setError("The request to get user location timed out.");
                    break;
                case error.UNKNOWN_ERROR:
                    setError("An unknown error occurred while retrieving your location.");
                    break;
                default:
                    setError("Error occurred while retrieving your location. Please try again later.");
            }
        };

        getLocation();
    }, []); // Empty dependency array ensures useEffect runs only on mount
    let lat = position.coords.latitude;
    let long = position.coords.longitude;
    return (
        <div>
            {error && <p>{error}</p>}
            {locationData && (
                <div>
                    <p>Latitude: {locationData.latitude}</p>
                    <p>Longitude: {locationData.longitude}</p>
                    <p>County: {locationData.county}</p>
                    {/* Display additional location data or components */}
                </div>
            )}
        </div>
    );
};

export default {city  };