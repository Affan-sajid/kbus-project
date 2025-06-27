# main.py - Flask backend for Bus Time Finder
# This file creates a simple API for the frontend to connect to.

from turtle import distance
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import math
import json
from findbus import AdvancedBusRouteFinder
app = Flask(__name__)
CORS(app, origins=['*'])  # Allow requests from any origin for development

# Health check route
@app.route('/')
def home():  
    return 'Bus Time Finder backend is running!'

# Endpoint to find bus routes between two places
@app.route('/find_buses', methods=['POST', 'OPTIONS'])
def find_buses():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    data = request.get_json()
    from_place = data.get('from', 'Unknown')
    to_place = data.get('to', 'Unknown')
    
    # Parse structured place data
    from_place_data = None
    to_place_data = None
    
    try:
        if data.get('fromPlaceData'):
            from_place_data = json.loads(data.get('fromPlaceData'))
        if data.get('toPlaceData'):
            to_place_data = json.loads(data.get('toPlaceData'))
    except json.JSONDecodeError as e:
        print(f"Error parsing place data: {e}")
    
    print(f"Route request: {from_place} → {to_place}")
    if from_place_data:
        print(f"From: {from_place_data.get('name')} ({from_place_data.get('place_id')}) at {from_place_data.get('coordinates')}")
    if to_place_data:
        print(f"To: {to_place_data.get('name')} ({to_place_data.get('place_id')}) at {to_place_data.get('coordinates')}")
        print(to_place_data.get('coordinates')["lat"])
    
    # Generate realistic sample data based on the locations
    finder = AdvancedBusRouteFinder()
    
    # Example: Find routes from Central Station area to University area
    origin_lat, origin_lon = 11.2588, 75.7804  # Near Central Station
    dest_lat, dest_lon = 11.1271, 75.8449      # Near University
    
    results = finder.find_routes_with_realtime(origin_lat, origin_lon, dest_lat, dest_lon)
    
    print("\n🚌 REAL-TIME BUS ROUTE RESULTS")
    print("=" * 60)

   
    for i, result in enumerate(results, 1):
        print(f"\nOption {i}:")
        print(f"Bus: {result['bus_name']}")
        print(f"Departure in: {result['departure_in']}")
        print(f"Next buses: {', '.join(result['next_buses'])}")
        print(f"Arrival: {result['arrival']}")
        print(f"Duration: {result['duration']}")
        print(f"Transfers: {result['transfers']}")
        print(f"Fare: {result['fare']}")
        print(f"Walking: {result['walking_distance']}")
        print("\nJourney Plan:")
        for j, step in enumerate(result['plan'], 1):
            print(f"  {j}. {step['type'].title()}: {step['distance']}")
        print("-" * 40)

    routes = []
    for i, result in enumerate(results, 1):
        plan = []
        for j , step in enumerate(result['plan'],1):
            singlplan = {'type': step['type'].title(), 'distance': step['distance']}            
            plan.append(singlplan)
        singleobj = {
            'bus_name': result['bus_name'],
            'departure_in': result['departure_in'],
            'arrival': result['arrival'],
            'duration': result['duration'],
            'transfers': result['transfers'],
            'fare': result['fare'],
            'plan': plan
        }
        routes.append(singleobj)

    
    # Sample bus routes with new structure
    
    
    response = jsonify({'routes': routes})
    response.headers.add('Access-Control-Allow-Origin', '*')
    print("send compledte")   

    return response

# Run the app (for development)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 



# sample_routes = [
#         {
#             'bus_name': 'onnamathe bus',
#             'departure_in': "10",
#             'arrival': "5:00 pm",
#             'duration': '1h 30m',
#             'transfers': "2",
#             'fare': '25',
#             'plan': [
#                 {'type': "bus", 'distance': "1km"},
#                 {'type': "auto", 'distance': "2km"},
#                 {'type': "walk", 'distance': "3km"},
#                 {'type': "taxi", 'distance': "4km"}
#             ]
#         },
#         {
#             'bus_name': 'randamathe bus',
#             'departure_in': "15",
#             'arrival': "5:30 pm",
#             'duration': '1h 10m',
#             'transfers': "1",
#             'fare': '30',
#             'plan': [
#                 {'type': "bus", 'distance': "2km"},
#                 {'type': "walk", 'distance': "1.5km"}
#             ]
#         },
#         {
#             'bus_name': 'moonnuamathe bus',
#             'departure_in': "20",
#             'arrival': "6:00 pm",
#             'duration': '1h 50m',
#             'transfers': "3",
#             'fare': '40',
#             'plan': [
#                 {'type': "bus", 'distance': "3km"},
#                 {'type': "auto", 'distance': "1km"},
#                 {'type': "walk", 'distance': "2km"},
#                 {'type': "auto", 'distance': "1km"}
#             ]
#         }
#     # 