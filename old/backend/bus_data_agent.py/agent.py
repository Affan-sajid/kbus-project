#!/usr/bin/env python3
"""
Bus Data Collection Agent using OpenAI
Collects bus stops, routes, and frequency data for a specific district
"""

import json
import requests
import time
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI
import dotenv
import os
dotenv.load_dotenv()
@dataclass
class BusStop:
    stop_id: str
    stop_name: str
    latitude: float
    longitude: float
    address: str
    landmark: str = ""
    district: str = ""

@dataclass
class BusRoute:
    route_id: str
    route_number: str
    route_name: str
    stops: List[str]  # List of stop_ids
    operator: str
    route_type: str  # ordinary, express, ac, non-ac
    frequency_minutes: int
    first_bus_time: str
    last_bus_time: str
    travel_time_between_stops: int

class BusDataCollectionAgent:
    def __init__(self, openai_api_key: str, district: str, state: str = "Kerala"):
        """
        Initialize the agent with OpenAI API key and target district
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.district = district
        self.state = state
        self.collected_stops = {}
        self.collected_routes = {}
        self.geocoding_cache = {}
        
    def get_district_bus_stops(self) -> List[Dict]:
        """
        Use OpenAI to generate a comprehensive list of bus stops in the district
        """
        prompt = f"""
        You are a local transportation expert for {self.district} district in {self.state}, India. 
        
        Generate a comprehensive list of major bus stops in {self.district} district. Include:
        1. Major bus stands/terminals
        2. Important junctions and intersections
        3. Hospitals, colleges, schools
        4. Markets and commercial areas
        5. Tourist spots and landmarks
        6. Railway stations (if any)
        7. Government offices
        8. Residential area stops
        
        For each bus stop, provide:
        - stop_name: Clear, commonly used name
        - address: Specific location/area within {self.district}
        - landmark: Notable nearby landmark
        - importance: (major/medium/minor)
        
        Format as JSON array with this structure:
        [
            {{
                "stop_name": "Central Bus Stand",
                "address": "Main Road, {self.district}",
                "landmark": "Near District Collectorate",
                "importance": "major"
            }}
        ]
        
        Provide the maximum amount or complete atleast a 100 stops covering different areas of {self.district} district.
        Only return the JSON array, no other text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a transportation data expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            # Clean the response to extract JSON
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                stops_data = json.loads(json_match.group())
                print(f"✅ Generated {len(stops_data)} bus stops for {self.district}")
                return stops_data
            else:
                print("❌ Could not extract JSON from OpenAI response")
                return []
                
        except Exception as e:
            print(f"❌ Error getting bus stops from OpenAI: {e}")
            return []
    
    def geocode_location(self, address: str, stop_name: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Geocode an address to get latitude and longitude
        Uses a combination of OpenStreetMap Nominatim (free) and fallback strategies
        """
        cache_key = f"{address}_{stop_name}"
        if cache_key in self.geocoding_cache:
            return self.geocoding_cache[cache_key]
        
        try:
            # Try OpenStreetMap Nominatim (free service)
            query = f"{stop_name}, {address}, {self.district}, {self.state}, India"
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'in'
            }
            
            headers = {'User-Agent': 'BusDataAgent/1.0'}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    self.geocoding_cache[cache_key] = (lat, lon)
                    time.sleep(1)  # Rate limiting
                    return lat, lon
            
            # Fallback: Use OpenAI to estimate coordinates
            lat, lon = self.estimate_coordinates_with_ai(stop_name, address)
            if lat and lon:
                self.geocoding_cache[cache_key] = (lat, lon)
                return lat, lon
                
        except Exception as e:
            print(f"⚠️  Geocoding error for {stop_name}: {e}")
        
        return None, None
    
    def estimate_coordinates_with_ai(self, stop_name: str, address: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Use OpenAI to estimate coordinates based on local knowledge
        """
        prompt = f"""
        You are a local geography expert for {self.district} district in {self.state}, India.
        
        Estimate the approximate latitude and longitude coordinates for:
        Stop Name: {stop_name}
        Address: {address}
        
        Consider the general location of {self.district} district and provide reasonable coordinates.
        
        Respond ONLY with coordinates in this exact format:
        latitude,longitude
        
        Example: 11.2588,75.7804
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a geography expert. Respond only with coordinates in format: lat,lon"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            content = response.choices[0].message.content.strip()
            coords = content.split(',')
            
            if len(coords) == 2:
                lat = float(coords[0].strip())
                lon = float(coords[1].strip())
                return lat, lon
                
        except Exception as e:
            print(f"⚠️  AI coordinate estimation error: {e}")
        
        return None, None
    
    def process_bus_stops(self, stops_data: List[Dict]) -> List[BusStop]:
        """
        Process raw stops data and geocode them
        """
        processed_stops = []
        
        print(f"🔄 Processing and geocoding {len(stops_data)} bus stops...")
        
        for i, stop_data in enumerate(stops_data, 1):
            print(f"  Processing stop {i}/{len(stops_data)}: {stop_data['stop_name']}")
            
            lat, lon = self.geocode_location(stop_data['address'], stop_data['stop_name'])
            
            if lat and lon:
                stop = BusStop(
                    stop_id=f"BS{i:03d}",
                    stop_name=stop_data['stop_name'],
                    latitude=lat,
                    longitude=lon,
                    address=stop_data['address'],
                    landmark=stop_data.get('landmark', ''),
                    district=self.district
                )
                processed_stops.append(stop)
                self.collected_stops[stop.stop_id] = stop
            else:
                print(f"  ⚠️  Could not geocode: {stop_data['stop_name']}")
        
        print(f"✅ Successfully processed {len(processed_stops)} bus stops")
        return processed_stops
    
    def generate_bus_routes(self, stops: List[BusStop]) -> List[Dict]:
        """
        Use OpenAI to generate realistic bus routes connecting the stops
        """
        stop_list = "\n".join([f"- {stop.stop_name} ({stop.stop_id})" for stop in stops])
        
        prompt = f"""
        You are a public transportation planning expert for {self.district} district in {self.state}, India.
        
        Given these bus stops in {self.district}:
        {stop_list}
        
        Generate realistic bus routes that would serve this district. Create routes that:
        1. Connect major stops with residential areas
        2. Provide circular routes for local connectivity
        3. Have express routes for longer distances
        4. Include both government (KSRTC) and private operators
        
        For each route, provide:
        - route_number: Real-style route number (like "1A", "2", "5E")
        - route_name: Descriptive name (like "Central - Airport Express")
        - stops: Array of stop_ids in order of travel
        - operator: "KSRTC", "Private", or specific operator name
        - route_type: "ordinary", "express", "ac", "limited"
        - frequency_minutes: Realistic frequency (15-60 minutes)
        - first_bus_time: "06:00" format
        - last_bus_time: "22:00" format
        - travel_time_between_stops: Minutes between consecutive stops (3-8)
        
        Create 8-12 diverse routes covering different areas.
        
        Format as JSON array:
        [
            {{
                "route_number": "1A",
                "route_name": "Central - Market Circular",
                "stops": ["BS001", "BS003", "BS005"],
                "operator": "KSRTC",
                "route_type": "ordinary",
                "frequency_minutes": 30,
                "first_bus_time": "06:00",
                "last_bus_time": "22:00",
                "travel_time_between_stops": 5
            }}
        ]
        
        Only return the JSON array, no other text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a transportation planning expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content.strip()
            # Clean the response to extract JSON
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                routes_data = json.loads(json_match.group())
                print(f"✅ Generated {len(routes_data)} bus routes for {self.district}")
                return routes_data
            else:
                print("❌ Could not extract JSON from OpenAI response")
                return []
                
        except Exception as e:
            print(f"❌ Error generating bus routes: {e}")
            return []
    
    def process_bus_routes(self, routes_data: List[Dict]) -> List[BusRoute]:
        """
        Process and validate bus routes data
        """
        processed_routes = []
        
        for i, route_data in enumerate(routes_data, 1):
            # Validate that all stops exist
            valid_stops = []
            for stop_id in route_data['stops']:
                if stop_id in self.collected_stops:
                    valid_stops.append(stop_id)
                else:
                    print(f"⚠️  Route {route_data['route_number']}: Unknown stop {stop_id}")
            
            if len(valid_stops) >= 2:  # Need at least 2 stops for a route
                route = BusRoute(
                    route_id=f"R{i:03d}",
                    route_number=route_data['route_number'],
                    route_name=route_data['route_name'],
                    stops=valid_stops,
                    operator=route_data['operator'],
                    route_type=route_data['route_type'],
                    frequency_minutes=route_data['frequency_minutes'],
                    first_bus_time=route_data['first_bus_time'],
                    last_bus_time=route_data['last_bus_time'],
                    travel_time_between_stops=route_data['travel_time_between_stops']
                )
                processed_routes.append(route)
                self.collected_routes[route.route_id] = route
        
        print(f"✅ Successfully processed {len(processed_routes)} bus routes")
        return processed_routes
    
    def export_data(self, filename: str = None) -> Dict:
        """
        Export collected data in the format expected by your bus route finder
        """
        if filename is None:
            filename = f"{self.district.lower()}_bus_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to the format expected by your algorithm
        export_data = {
            "bus_stops": [],
            "bus_routes": []
        }
        
        # Export stops
        for stop in self.collected_stops.values():
            export_data["bus_stops"].append({
                "stop_id": stop.stop_id,
                "stop_name": stop.stop_name,
                "latitude": stop.latitude,
                "longitude": stop.longitude,
                "address": stop.address,
                "landmark": stop.landmark,
                "district": stop.district
            })
        
        # Export routes
        for route in self.collected_routes.values():
            export_data["bus_routes"].append({
                "route_id": route.route_id,
                "route_number": route.route_number,
                "route_name": route.route_name,
                "stops": route.stops,
                "operator": route.operator,
                "route_type": route.route_type,
                "frequency_minutes": route.frequency_minutes,
                "first_bus_time": route.first_bus_time,
                "last_bus_time": route.last_bus_time,
                "travel_time_between_stops": route.travel_time_between_stops
            })
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Data exported to {filename}")
        print(f"📊 Summary: {len(export_data['bus_stops'])} stops, {len(export_data['bus_routes'])} routes")
        
        return export_data
    
    def run_full_collection(self) -> Dict:
        """
        Run the complete data collection process
        """
        print(f"🚌 Starting bus data collection for {self.district} district, {self.state}")
        print("=" * 60)
        
        # Step 1: Get bus stops from OpenAI
        print("\n🔄 Step 1: Generating bus stops using OpenAI...")
        stops_data = self.get_district_bus_stops()
        
        if not stops_data:
            print("❌ Failed to generate bus stops. Exiting.")
            return {}
        
        # Step 2: Process and geocode stops
        print("\n🔄 Step 2: Processing and geocoding stops...")
        processed_stops = self.process_bus_stops(stops_data)
        
        if not processed_stops:
            print("❌ No stops could be processed. Exiting.")
            return {}
        
        # Step 3: Generate routes
        print("\n🔄 Step 3: Generating bus routes using OpenAI...")
        routes_data = self.generate_bus_routes(processed_stops)
        
        if not routes_data:
            print("❌ Failed to generate bus routes. Exiting.")
            return {}
        
        # Step 4: Process routes
        print("\n🔄 Step 4: Processing bus routes...")
        processed_routes = self.process_bus_routes(routes_data)
        
        # Step 5: Export data
        print("\n🔄 Step 5: Exporting data...")
        final_data = self.export_data()
        
        print("\n✅ Bus data collection completed successfully!")
        return final_data





def main():
    """
    Example usage of the Bus Data Collection Agent
    """
    # Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Replace with your OpenAI API key
    DISTRICT = "Kozhikode"  # Change to your target district
    STATE = "Kerala"        # Change to your target state
    
    # Create agent
    agent = BusDataCollectionAgent(
        openai_api_key=OPENAI_API_KEY,
        district=DISTRICT,
        state=STATE
    )
    
    # Run collection
    data = agent.run_full_collection()
    
    # Display summary
    if data:
        print("\n📋 Collection Summary:")
        print(f"District: {DISTRICT}, {STATE}")
        print(f"Bus Stops: {len(data.get('bus_stops', []))}")
        print(f"Bus Routes: {len(data.get('bus_routes', []))}")
        print("\nData file created and ready for use with your bus route finder!")

if __name__ == "__main__":
    main()