#!/usr/bin/env python3
"""
Advanced Bus Route Finder with Real-Time Scheduling
Implements complete pathfinding with live bus timing information
"""

import json
import math
import heapq
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field

def load_bus_data_from_files(stops_file="backend/bus_stops.json", routes_file="backend/bus_routes.json"):
    """Load and format bus data from external JSON files"""
    try:
        # Load bus stops
        with open(stops_file, 'r', encoding='utf-8') as f:
            stops_data = json.load(f)
        
        # Handle different JSON structures for stops
        if isinstance(stops_data, list):
            bus_stops = stops_data
        elif 'bus_stops' in stops_data:
            bus_stops = stops_data['bus_stops']
        elif 'stops' in stops_data:
            bus_stops = stops_data['stops']
        else:
            bus_stops = list(stops_data.values())
        
        # Load bus routes
        with open(routes_file, 'r', encoding='utf-8') as f:
            routes_data = json.load(f)
        
        # Handle different JSON structures for routes
        if isinstance(routes_data, list):
            bus_routes = routes_data
        elif 'bus_routes' in routes_data:
            bus_routes = routes_data['bus_routes']
        elif 'routes' in routes_data:
            bus_routes = routes_data['routes']
        else:
            bus_routes = list(routes_data.values())
        
        # Format routes with defaults for missing fields
        formatted_routes = []
        for route in bus_routes:
            formatted_route = {
                "route_id": route.get("route_id", f"R{len(formatted_routes)+1:03d}"),
                "route_number": route.get("route_number", route.get("route_id", "Unknown")),
                "route_name": route.get("route_name", f"Route {route.get('route_number', 'Unknown')}"),
                "stops": route.get("stops", []),
                "operator": route.get("operator", "Unknown"),
                "route_type": route.get("route_type", "ordinary"),
                "frequency_minutes": route.get("frequency_minutes", 30),
                "first_bus_time": route.get("first_bus_time", "06:00"),
                "last_bus_time": route.get("last_bus_time", "22:00"),
                "travel_time_between_stops": route.get("travel_time_between_stops", 5)
            }
            formatted_routes.append(formatted_route)
        
        return {
            "bus_stops": bus_stops,
            "bus_routes": formatted_routes
        }
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None

# Load data from files
BUS_DATA = load_bus_data_from_files()
print(BUS_DATA)

# Sample data with enhanced scheduling information


@dataclass
class BusSchedule:
    """Real-time bus schedule information"""
    route_id: str
    route_number: str
    next_departure: datetime
    next_arrival: datetime
    subsequent_departures: List[datetime]
    subsequent_arrivals: List[datetime]
    minutes_until_next: int

@dataclass
class RouteSegment:
    """Represents one segment of a journey (single bus ride)"""
    route_id: str
    route_number: str
    route_name: str
    operator: str
    from_stop_id: str
    to_stop_id: str
    from_stop_name: str
    to_stop_name: str
    duration_minutes: int
    stops_count: int
    fare: float
    route_type: str
    schedule: BusSchedule  # Real-time schedule info

@dataclass
class Journey:
    """Complete journey from origin to destination with real-time info"""
    segments: List[RouteSegment]
    total_duration: int
    total_transfers: int
    total_fare: float
    walking_distance: float
    total_stops: int
    journey_score: float
    departure_time: datetime
    arrival_time: datetime
    next_departure_in_minutes: int
    
    def __post_init__(self):
        self.total_transfers = len(self.segments) - 1
        self.total_stops = sum(seg.stops_count for seg in self.segments)
        self.total_fare = sum(seg.fare for seg in self.segments)

@dataclass
class PathState:
    """State in pathfinding algorithm"""
    current_stop: str
    total_cost: float
    total_duration: int
    transfers: int
    segments: List[RouteSegment]
    visited_routes: Set[str]
    current_time: datetime
    
    def __lt__(self, other):
        if self.total_cost != other.total_cost:
            return self.total_cost < other.total_cost
        return self.transfers < other.transfers

class AdvancedBusRouteFinder:
    def __init__(self):
        self.stops = {}
        self.routes = {}
        self.stop_routes = {}
        self.route_graph = {}
        self.current_time = datetime.now()
        self.load_BUS_DATA()
        self.build_route_graph()
    
    def load_BUS_DATA(self):
        """Load the sample data into our structures"""
        print("🔄 Loading bus network data...")
        
        for stop_data in BUS_DATA["bus_stops"]:
            self.stops[stop_data["stop_id"]] = stop_data
        
        for route_data in BUS_DATA["bus_routes"]:
            self.routes[route_data["route_id"]] = route_data
            
            for stop_id in route_data["stops"]:
                if stop_id not in self.stop_routes:
                    self.stop_routes[stop_id] = []
                self.stop_routes[stop_id].append(route_data["route_id"])
        
        print(f"✅ Loaded {len(self.stops)} stops, {len(self.routes)} routes")
    
    def get_next_bus_times(self, route_id: str, from_stop_id: str) -> BusSchedule:
        """Calculate next bus times for a specific route and stop"""
       
        current_time = self.current_time
        
        route = self.routes[route_id]
        
        # Parse first bus time
        first_bus_hour, first_bus_minute = map(int, route["first_bus_time"].split(":"))
        last_bus_hour, last_bus_minute = map(int, route["last_bus_time"].split(":"))
        
        # Create first bus datetime for today
        today = current_time.date()
        first_bus_today = datetime.combine(today, datetime.min.time().replace(
            hour=first_bus_hour, minute=first_bus_minute
        ))
        last_bus_today = datetime.combine(today, datetime.min.time().replace(
            hour=last_bus_hour, minute=last_bus_minute
        ))
        
        # If current time is before first bus, start from first bus
        if current_time < first_bus_today:
            reference_time = first_bus_today
        else:
            # Find next bus based on frequency
            minutes_since_first = int((current_time - first_bus_today).total_seconds() / 60)
            buses_passed = minutes_since_first // route["frequency_minutes"]
            next_bus_minutes = (buses_passed + 1) * route["frequency_minutes"]
            reference_time = first_bus_today + timedelta(minutes=next_bus_minutes)
        
        # If next bus is after last bus, move to next day
        if reference_time > last_bus_today:
            tomorrow = today + timedelta(days=1)
            first_bus_tomorrow = datetime.combine(tomorrow, datetime.min.time().replace(
                hour=first_bus_hour, minute=first_bus_minute
            ))
            reference_time = first_bus_tomorrow
        
        # Calculate travel time to the specific stop
        stop_index = route["stops"].index(from_stop_id) if from_stop_id in route["stops"] else 0
        travel_time_to_stop = stop_index * route["travel_time_between_stops"]
        
        # Next bus departure and arrival
        next_departure = reference_time + timedelta(minutes=travel_time_to_stop)
        next_arrival = next_departure + timedelta(minutes=route["travel_time_between_stops"])
        
        # Calculate subsequent buses (next 2-3 buses)
        subsequent_departures = []
        subsequent_arrivals = []
        
        for i in range(1, 4):  # Next 3 buses
            future_departure = reference_time + timedelta(minutes=i * route["frequency_minutes"] + travel_time_to_stop)
            future_arrival = future_departure + timedelta(minutes=route["travel_time_between_stops"])
            
            # Check if it's still within service hours
            future_day_last_bus = datetime.combine(future_departure.date(), datetime.min.time().replace(
                hour=last_bus_hour, minute=last_bus_minute
            ))
            
            if future_departure <= future_day_last_bus:
                subsequent_departures.append(future_departure)
                subsequent_arrivals.append(future_arrival)
        
        minutes_until_next = max(0, int((next_departure - current_time).total_seconds() / 60))
        
        return BusSchedule(
            route_id=route_id,
            route_number=route["route_number"],
            next_departure=next_departure,
            next_arrival=next_arrival,
            subsequent_departures=subsequent_departures,
            subsequent_arrivals=subsequent_arrivals,
            minutes_until_next=minutes_until_next
        )
    
    def build_route_graph(self):
        """Build a graph representation with real-time scheduling"""
        print("🔄 Building route network graph with real-time data...")
        
        self.route_graph = {}
        
        for stop_id in self.stops.keys():
            self.route_graph[stop_id] = []
            
            for route_id in self.stop_routes.get(stop_id, []):
                route = self.routes[route_id]
                
                if stop_id in route["stops"]:
                    current_idx = route["stops"].index(stop_id)
                    
                    for target_idx in range(current_idx + 1, len(route["stops"])):
                        target_stop = route["stops"][target_idx]
                        
                        if target_stop == stop_id:
                            continue
                        
                        # Get real-time schedule
                        schedule = self.get_next_bus_times(route_id, stop_id)
                        
                        duration = self.calculate_segment_duration(route_id, current_idx, target_idx)
                        fare = self.calculate_segment_fare(route_id, current_idx, target_idx)
                        
                        segment = RouteSegment(
                            route_id=route_id,
                            route_number=route["route_number"],
                            route_name=route["route_name"],
                            operator=route["operator"],
                            from_stop_id=stop_id,
                            to_stop_id=target_stop,
                            from_stop_name=self.stops[stop_id]["stop_name"],
                            to_stop_name=self.stops[target_stop]["stop_name"],
                            duration_minutes=duration,
                            stops_count=target_idx - current_idx,
                            fare=fare,
                            route_type=route["route_type"],
                            schedule=schedule
                        )
                        
                        self.route_graph[stop_id].append(segment)
        
        print("✅ Route graph built with real-time scheduling")
    
    def calculate_segment_duration(self, route_id: str, from_idx: int, to_idx: int) -> int:
        """Calculate duration for a route segment"""
        route = self.routes[route_id]
        stops_count = to_idx - from_idx
        
        return stops_count * route["travel_time_between_stops"]
    
    def calculate_segment_fare(self, route_id: str, from_idx: int, to_idx: int) -> float:
        """Calculate fare for a route segment"""
        route = self.routes[route_id]
        stops_count = to_idx - from_idx
        
        if route["route_type"] == "express":
            base_fare = 15.0
            per_stop = 2.0
        else:
            base_fare = 8.0
            per_stop = 1.5
        
        return base_fare + (stops_count * per_stop)
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between coordinates using Haversine formula"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def find_nearest_stops(self, lat: float, lon: float, max_distance: float = 1000) -> List[Tuple[str, float]]:
        """Find nearest bus stops to given coordinates"""
        nearby_stops = []
        
        for stop_id, stop_data in self.stops.items():
            distance = self.calculate_distance(lat, lon, stop_data["latitude"], stop_data["longitude"])
            if distance <= max_distance:
                nearby_stops.append((stop_id, distance))
        
        nearby_stops.sort(key=lambda x: x[1])
        return nearby_stops[:3]
    
    def format_journey_output(self, journey: Journey) -> Dict:
        """Format journey in the requested output structure"""
        # Get the first segment for bus name and departure info
        first_segment = journey.segments[0]
        
        # Create plan with different transport modes
        plan = []
        walking_added = False
        
        for i, segment in enumerate(journey.segments):
            # Add walking segment before first bus (if walking distance > 0)
            if i == 0 and journey.walking_distance > 0 and not walking_added:
                plan.append({
                    'type': 'walk',
                    'distance': f"{journey.walking_distance:.0f}m"
                })
                walking_added = True
            
            # Add bus segment
            plan.append({
                'type': 'bus',
                'distance': f"{segment.stops_count * 2}km",  # Approximate distance
                'route_number': segment.route_number,
                'from': segment.from_stop_name,
                'to': segment.to_stop_name,
                'operator': segment.operator
            })
            
            # Add transfer segments (auto/taxi) between buses
            if i < len(journey.segments) - 1:
                plan.append({
                    'type': 'auto',  # Could be 'taxi' based on distance
                    'distance': '500m'  # Transfer distance
                })
        
        # Format subsequent bus times
        subsequent_times = []
        for i, dept_time in enumerate(first_segment.schedule.subsequent_departures[:2]):
            minutes_from_now = int((dept_time - self.current_time).total_seconds() / 60)
            subsequent_times.append(f"{minutes_from_now} minutes")
        
        return {
            'bus_name': f"{first_segment.route_number} - {first_segment.route_name}",
            'departure_in': f"{first_segment.schedule.minutes_until_next}",
            'next_buses': subsequent_times,  # Next 2 buses
            'arrival': journey.arrival_time.strftime("%I:%M %p"),
            'duration': f"{journey.total_duration // 60}h {journey.total_duration % 60}m",
            'transfers': str(journey.total_transfers),
            'fare': f"₹{journey.total_fare:.0f}",
            'walking_distance': f"{journey.walking_distance:.0f}m",
            'plan': plan
        }
    
    def find_routes_with_realtime(self, origin_lat: float, origin_lon: float, 
                                 dest_lat: float, dest_lon: float, 
                                 max_transfers: int = 2,max_walkingsdis: int = 1000) -> List[Dict]:
        """Find routes and return in the requested format"""
        print("🔍 Finding routes with real-time information...")
        
        # Update current time
        self.current_time = datetime.now()
        
        # Rebuild graph with current time
        self.build_route_graph()
        
        # Find nearest stops
        origin_stops = self.find_nearest_stops(origin_lat, origin_lon, max_walkingsdis)
        dest_stops = self.find_nearest_stops(dest_lat, dest_lon, max_walkingsdis)
        
        if not origin_stops or not dest_stops:
            return []
        
        all_journeys = []
        
        # Simple pathfinding for demo (can be enhanced with full Dijkstra)
        for origin_stop_id, origin_walking_dist in origin_stops[:2]:  # Limit for performance
            for dest_stop_id, dest_walking_dist in dest_stops[:2]:
                
                if origin_stop_id == dest_stop_id:
                    continue
                
                # Find direct routes first
                journeys = self.find_direct_routes(origin_stop_id, dest_stop_id, origin_walking_dist, dest_walking_dist)
                all_journeys.extend(journeys)
        
        # Sort by departure time and quality
        all_journeys.sort(key=lambda x: (x.next_departure_in_minutes, x.journey_score))
        
        # Format output
        formatted_results = []
        for journey in all_journeys[:5]:  # Top 5 results
            formatted_results.append(self.format_journey_output(journey))
        
        return formatted_results
    
    def find_direct_routes(self, origin_stop: str, dest_stop: str, origin_walking: float, dest_walking: float) -> List[Journey]:
        """Find direct routes between two stops"""
        journeys = []
        
        # Check all routes from origin stop
        for segment in self.route_graph.get(origin_stop, []):
            if segment.to_stop_id == dest_stop:
                # Direct route found
                journey = Journey(
                    segments=[segment],
                    total_duration=segment.duration_minutes + segment.schedule.minutes_until_next,
                    total_transfers=0,
                    total_fare=segment.fare,
                    walking_distance=origin_walking + dest_walking,
                    total_stops=segment.stops_count,
                    journey_score=0,
                    departure_time=segment.schedule.next_departure,
                    arrival_time=segment.schedule.next_arrival,
                    next_departure_in_minutes=segment.schedule.minutes_until_next
                )
                
                journey.journey_score = self.calculate_journey_score(
                    journey.total_duration, journey.total_transfers, 
                    journey.total_fare, journey.walking_distance
                )
                
                journeys.append(journey)
        
        return journeys
    
    def calculate_journey_score(self, duration: int, transfers: int, fare: float, walking_distance: float) -> float:
        """Calculate overall journey score for ranking"""
        duration_weight = 1.0
        transfer_weight = 20.0
        fare_weight = 0.5
        walking_weight = 0.01
        
        return (duration * duration_weight + 
                transfers * transfer_weight + 
                fare * fare_weight + 
                walking_distance * walking_weight)

# Example usage and testing
def main():
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
            singlplan = {f'type': {step['type'].title()}, 'distance': {step['distance']}}
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

if __name__ == "__main__":
    main()