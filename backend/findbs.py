SAMPLE_DATA = {
    "bus_stops": [
        {
            "stop_id": "BS001",
            "stop_name": "Central Station",
            "latitude": 11.2588,
            "longitude": 75.7804,
            "address": "Central Station Rd, Kozhikode"
        },
        {
            "stop_id": "BS002", 
            "stop_name": "Medical College",
            "latitude": 11.2496,
            "longitude": 75.7666,
            "address": "Medical College Rd, Kozhikode"
        },
        {
            "stop_id": "BS003",
            "stop_name": "Palayam Market",
            "latitude": 11.2588,
            "longitude": 75.7714,
            "address": "Palayam, Kozhikode"
        },
        {
            "stop_id": "BS004",
            "stop_name": "Beach Road",
            "latitude": 11.2750,
            "longitude": 75.7747,
            "address": "Beach Rd, Kozhikode"
        },
        {
            "stop_id": "BS005",
            "stop_name": "University",
            "latitude": 11.1271,
            "longitude": 75.8449,
            "address": "Calicut University, Malappuram"
        },
        {
            "stop_id": "BS006",
            "stop_name": "Airport Junction",
            "latitude": 11.1410,
            "longitude": 75.9550,
            "address": "Airport Rd, Kozhikode"
        },
        {
            "stop_id": "BS007",
            "stop_name": "Private Bus Stand",
            "latitude": 11.2480,
            "longitude": 75.7763,
            "address": "Mavoor Rd, Kozhikode"
        },
        {
            "stop_id": "BS008",
            "stop_name": "KSRTC Bus Stand",
            "latitude": 11.2447,
            "longitude": 75.7730,
            "address": "Mavoor Rd, Kozhikode"
        }
    ],
    "bus_routes": [
        {
            "route_id": "R001",
            "route_number": "1A",
            "route_name": "Central Station - Airport",
            "stops": ["BS001", "BS003", "BS002", "BS005", "BS006"],
            "operator": "KSRTC",
            "route_type": "ordinary",
            "frequency_minutes": 30
        },
        {
            "route_id": "R002", 
            "route_number": "1B",
            "route_name": "Airport - Central Station",
            "stops": ["BS006", "BS005", "BS002", "BS003", "BS001"],
            "operator": "KSRTC",
            "route_type": "ordinary",
            "frequency_minutes": 30
        },
        {
            "route_id": "R003",
            "route_number": "2",
            "route_name": "Beach Road Circular",
            "stops": ["BS001", "BS004", "BS003", "BS007", "BS008", "BS001"],
            "operator": "Private",
            "route_type": "ordinary",
            "frequency_minutes": 20
        },
        {
            "route_id": "R004",
            "route_number": "5E",
            "route_name": "Express - Central to University",
            "stops": ["BS001", "BS002", "BS005"],
            "operator": "KSRTC",
            "route_type": "express",
            "frequency_minutes": 60
        },
        {
            "route_id": "R005",
            "route_number": "5E-R",
            "route_name": "Express - University to Central",
            "stops": ["BS005", "BS002", "BS001"],
            "operator": "KSRTC",
            "route_type": "express",
            "frequency_minutes": 60
        },
        {
            "route_id": "R006",
            "route_number": "3",
            "route_name": "Medical College - Beach Road",
            "stops": ["BS002", "BS003", "BS004"],
            "operator": "Private",
            "route_type": "ordinary",
            "frequency_minutes": 45
        }
    ]
}
st

for stop_data in SAMPLE_DATA["bus_stops"]:
    stops[]


