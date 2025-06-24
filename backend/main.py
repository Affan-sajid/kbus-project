# main.py - Flask backend for Bus Time Finder
# This file creates a simple API for the frontend to connect to.

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from the frontend (localhost, etc.)

# Health check route
@app.route('/')
def home():  
    return 'Bus Time Finder backend is running!'

# Endpoint to find bus routes between two places
@app.route('/find_buses', methods=['POST'])
def find_buses():
    data = request.get_json()
    from_place = data.get('from')
    to_place = data.get('to')

    # For now, return mock data (replace with real logic later)
    mock_routes = [
        {
            'bus_number': 'Bus Nº 31',
            'route': f'{from_place} → {to_place}',
            'departure': '16:00',
            'arrival': '17:00',
            'duration': '1h',
            'transfers': 0,
            'fare': '₹30'
        },
        {
            'bus_number': 'Central Line',
            'route': f'{from_place} → C → {to_place}',
            'departure': '16:15',
            'arrival': '17:30',
            'duration': '1h 15m',
            'transfers': 1,
            'fare': '₹25'
        },
        {
            'bus_number': 'Tram Nº 17',
            'route': f'{from_place} → D → {to_place}',
            'departure': '16:20',
            'arrival': '17:40',
            'duration': '1h 20m',
            'transfers': 2,
            'fare': '₹20'
        },
    ]
    return jsonify({'routes': mock_routes})

# Run the app (for development)
if __name__ == '__main__':
    app.run(debug=True)




