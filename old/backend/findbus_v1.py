#!/usr/bin/env python3
"""
Advanced Bus Route Finder with Complete Pathfinding Algorithm
Implements Dijkstra's algorithm for finding optimal routes with transfers
"""

import json
import math
import heapq
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field

# Sample data embedded in the code
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

@dataclass
class Journey:
    """Complete journey from origin to destination"""
    segments: List[RouteSegment]
    total_duration: int
    total_transfers: int
    total_fare: float
    walking_distance: float
    total_stops: int
    journey_score: float
    
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
    
    def __lt__(self, other):
        """Enable comparison for heapq - compare by total_cost first, then by transfers"""
        if self.total_cost != other.total_cost:
            return self.total_cost < other.total_cost
        return self.transfers < other.transfers

class AdvancedBusRouteFinder:
    def __init__(self):
        self.stops = {}
        self.routes = {}
        self.stop_routes = {}  # stop_id -> list of route_ids
        self.route_graph = {}  # Precomputed graph for faster pathfinding
        self.load_sample_data()
        self.build_route_graph()
    
    def load_sample_data(self):
        """Load the sample data into our structures"""
        print("🔄 Loading bus network data...")
        
        # Load stops
        for stop_data in SAMPLE_DATA["bus_stops"]:
            self.stops[stop_data["stop_id"]] = stop_data
        
        # Load routes and build stop_routes mapping
        for route_data in SAMPLE_DATA["bus_routes"]:
            self.routes[route_data["route_id"]] = route_data
            
            # Map each stop to routes that pass through it
            for stop_id in route_data["stops"]:
                if stop_id not in self.stop_routes:
                    self.stop_routes[stop_id] = []
                self.stop_routes[stop_id].append(route_data["route_id"])
        
        print(f"✅ Loaded {len(self.stops)} stops, {len(self.routes)} routes")
    
    def build_route_graph(self):
        """Build a graph representation for faster pathfinding"""
        print("🔄 Building route network graph...")
        
        self.route_graph = {}
        
        # For each stop, find all directly reachable stops via each route
        for stop_id in self.stops.keys():
            self.route_graph[stop_id] = []
            
            # Check all routes passing through this stop
            for route_id in self.stop_routes.get(stop_id, []):
                route = self.routes[route_id]
                
                # Find position of current stop in route
                if stop_id in route["stops"]:
                    current_idx = route["stops"].index(stop_id)
                    
                    # Add all reachable stops on this route
                    for target_idx in range(current_idx + 1, len(route["stops"])):
                        target_stop = route["stops"][target_idx]
                        
                        # Skip if it's the same stop (for circular routes)
                        if target_stop == stop_id:
                            continue
                            
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
                            route_type=route["route_type"]
                        )
                        
                        self.route_graph[stop_id].append(segment)
        
        print("✅ Route graph built successfully")
    
    def calculate_segment_duration(self, route_id: str, from_idx: int, to_idx: int) -> int:
        """Calculate duration for a route segment"""
        route = self.routes[route_id]
        stops_count = to_idx - from_idx
        
        # Base time per stop + route type modifier
        if route["route_type"] == "express":
            time_per_stop = 2  # Express buses are faster
        else:
            time_per_stop = 3  # Regular buses
        
        # Add frequency-based waiting time (half of frequency)
        waiting_time = route["frequency_minutes"] // 2
        
        return (stops_count * time_per_stop) + waiting_time
    
    def calculate_segment_fare(self, route_id: str, from_idx: int, to_idx: int) -> float:
        """Calculate fare for a route segment"""
        route = self.routes[route_id]
        stops_count = to_idx - from_idx
        
        # Base fare + per-stop charge
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
        return nearby_stops[:3]  # Return top 3 nearest
    
    def calculate_journey_score(self, duration: int, transfers: int, fare: float, walking_distance: float) -> float:
        """Calculate overall journey score for ranking"""
        # Weighted scoring (lower is better)
        duration_weight = 1.0
        transfer_weight = 20.0  # Heavy penalty for transfers
        fare_weight = 0.5
        walking_weight = 0.01
        
        return (duration * duration_weight + 
                transfers * transfer_weight + 
                fare * fare_weight + 
                walking_distance * walking_weight)
    
    def find_all_routes(self, origin_lat: float, origin_lon: float, 
                       dest_lat: float, dest_lon: float, 
                       max_transfers: int = 3, max_walking_distance: float = 1000) -> List[Journey]:
        """
        Complete pathfinding algorithm using modified Dijkstra's algorithm
        Finds all possible routes with comprehensive transfer options
        """
        print("🔍 Finding optimal routes...")
        
        # Step 1: Find nearest stops to origin and destination
        origin_stops = self.find_nearest_stops(origin_lat, origin_lon, max_walking_distance)
        dest_stops = self.find_nearest_stops(dest_lat, dest_lon, max_walking_distance)
        
        if not origin_stops or not dest_stops:
            print("❌ No nearby bus stops found!")
            return []
        
        print(f"📍 Found {len(origin_stops)} origin stops, {len(dest_stops)} destination stops")
        
        all_journeys = []
        
        # Step 2: Find routes from each origin stop to each destination stop
        for origin_stop_id, origin_walking_dist in origin_stops:
            for dest_stop_id, dest_walking_dist in dest_stops:
                
                if origin_stop_id == dest_stop_id:
                    continue  # Skip same stop
                
                print(f"🔍 Searching: {self.stops[origin_stop_id]['stop_name']} → {self.stops[dest_stop_id]['stop_name']}")
                
                # Use Dijkstra's algorithm for pathfinding
                journeys = self.dijkstra_pathfind(origin_stop_id, dest_stop_id, max_transfers)
                
                # Add walking distances to journeys
                for journey in journeys:
                    journey.walking_distance = origin_walking_dist + dest_walking_dist
                    journey.journey_score = self.calculate_journey_score(
                        journey.total_duration, journey.total_transfers, 
                        journey.total_fare, journey.walking_distance
                    )
                
                all_journeys.extend(journeys)
        
        # Step 3: Filter and rank all journeys
        return self.filter_and_rank_journeys(all_journeys, max_transfers)
    
    def dijkstra_pathfind(self, origin_stop: str, dest_stop: str, max_transfers: int) -> List[Journey]:
        """
        Dijkstra's algorithm implementation for bus route pathfinding
        """
        # Priority queue: (total_cost, current_stop, path_state)
        pq = [(0, origin_stop, PathState(
            current_stop=origin_stop,
            total_cost=0,
            total_duration=0,
            transfers=0,
            segments=[],
            visited_routes=set()
        ))]
        
        # Track best cost to reach each (stop, transfer_count) state
        best_costs = {}
        found_journeys = []
        
        while pq:
            current_cost, current_stop, state = heapq.heappop(pq)
            
            # Skip if we've exceeded transfer limit
            if state.transfers > max_transfers:
                continue
            
            # Check if we've reached destination
            if current_stop == dest_stop and state.segments:
                journey = Journey(
                    segments=state.segments.copy(),
                    total_duration=state.total_duration,
                    total_transfers=state.transfers,
                    total_fare=0,  # Will be calculated in __post_init__
                    walking_distance=0,  # Will be added later
                    total_stops=0,  # Will be calculated in __post_init__
                    journey_score=0  # Will be calculated later
                )
                found_journeys.append(journey)
                continue
            
            # Pruning: skip if we've found a better path to this state
            state_key = (current_stop, state.transfers)
            if state_key in best_costs and best_costs[state_key] < current_cost:
                continue
            best_costs[state_key] = current_cost
            
            # Explore all possible next segments from current stop
            for segment in self.route_graph.get(current_stop, []):
                
                # Skip if this would create a loop (visiting same route again)
                if segment.route_id in state.visited_routes:
                    continue
                
                # Calculate new state
                new_transfers = state.transfers
                new_visited_routes = state.visited_routes.copy()
                
                # If this is a different route than the last one, it's a transfer
                if state.segments and state.segments[-1].route_id != segment.route_id:
                    new_transfers += 1
                
                new_visited_routes.add(segment.route_id)
                
                new_state = PathState(
                    current_stop=segment.to_stop_id,
                    total_cost=current_cost + segment.duration_minutes + (new_transfers * 15),  # Transfer penalty
                    total_duration=state.total_duration + segment.duration_minutes,
                    transfers=new_transfers,
                    segments=state.segments + [segment],
                    visited_routes=new_visited_routes
                )
                
                heapq.heappush(pq, (new_state.total_cost, segment.to_stop_id, new_state))
        
        return found_journeys
    
    def filter_and_rank_journeys(self, journeys: List[Journey], max_transfers: int) -> List[Journey]:
        """Filter impractical routes and rank by quality"""
        if not journeys:
            return []
        
        print(f"🔍 Filtering from {len(journeys)} possible journeys...")
        
        # Step 1: Basic filtering
        filtered = []
        for journey in journeys:
            # Filter criteria
            if (journey.total_transfers <= max_transfers and 
                journey.total_duration <= 180 and  # Max 3 hours
                journey.walking_distance <= 2000):  # Max 2km walking
                filtered.append(journey)
        
        if not filtered:
            return []
        
        # Step 2: Remove dominated routes
        # A route is dominated if another route is better in all aspects
        non_dominated = []
        for i, journey1 in enumerate(filtered):
            is_dominated = False
            for j, journey2 in enumerate(filtered):
                if i != j:
                    if (journey2.total_duration <= journey1.total_duration and
                        journey2.total_transfers <= journey1.total_transfers and
                        journey2.total_fare <= journey1.total_fare and
                        journey2.walking_distance <= journey1.walking_distance and
                        (journey2.total_duration < journey1.total_duration or
                         journey2.total_transfers < journey1.total_transfers or
                         journey2.total_fare < journey1.total_fare or
                         journey2.walking_distance < journey1.walking_distance)):
                        is_dominated = True
                        break
            
            if not is_dominated:
                non_dominated.append(journey1)
        
        # Step 3: Sort by journey score (lower is better)
        non_dominated.sort(key=lambda x: x.journey_score)
        
        print(f"✅ Filtered to {len(non_dominated)} optimal journeys")
        return non_dominated[:10]  # Return top 10
    
    def search_stops_by_name(self, query: str) -> List[Dict]:
        """Search bus stops by name"""
        results = []
        query_lower = query.lower()
        
        for stop_id, stop_data in self.stops.items():
            if query_lower in stop_data["stop_name"].lower():
                results.append({
                    "stop_id": stop_id,
                    "stop_name": stop_data["stop_name"],
                    "address": stop_data["address"]
                })
        
        return results

def print_header():
    """Print application header"""
    print("=" * 70)
    print("🚌 ADVANCED BUS ROUTE FINDER - COMPLETE PATHFINDING ALGORITHM")
    print("=" * 70)

def print_menu():
    """Print main menu options"""
    print("\nChoose an option:")
    print("1. Find routes between coordinates (Full Algorithm)")
    print("2. Find routes between bus stops (Full Algorithm)")
    print("3. Search bus stops by name")
    print("4. Show all bus stops")
    print("5. Exit")
    print("-" * 50)

def print_detailed_journeys(journeys: List[Journey], finder):
    """Print journeys with complete details"""
    if not journeys:
        print("❌ No routes found!")
        return
    
    print(f"\n🎯 Found {len(journeys)} optimal route(s):")
    print("=" * 80)
    
    for i, journey in enumerate(journeys, 1):
        print(f"\n🚌 ROUTE OPTION {i}")
        print(f"⏱️  Total Duration: {journey.total_duration} minutes")
        print(f"🔄 Transfers: {journey.total_transfers}")
        print(f"💰 Total Fare: ₹{journey.total_fare:.2f}")
        print(f"🚶 Walking Distance: {journey.walking_distance:.0f}m")
        print(f"📊 Quality Score: {journey.journey_score:.1f} (lower is better)")
        print("-" * 50)
        
        for j, segment in enumerate(journey.segments, 1):
            print(f"  Segment {j}: {segment.route_number} - {segment.route_name}")
            print(f"  🚏 {segment.from_stop_name} → {segment.to_stop_name}")
            print(f"  🏢 Operator: {segment.operator} | Type: {segment.route_type}")
            print(f"  ⏱️  Duration: {segment.duration_minutes} min | Stops: {segment.stops_count} | Fare: ₹{segment.fare:.2f}")
            
            if j < len(journey.segments):
                print(f"  🔄 Transfer at: {segment.to_stop_name}")
            print()
        
        print("=" * 50)

def get_coordinates():
    """Get coordinates from user input"""
    try:
        print("Enter coordinates (latitude, longitude):")
        lat = float(input("Latitude: "))
        lon = float(input("Longitude: "))
        return lat, lon
    except ValueError:
        print("❌ Invalid coordinates! Please enter numbers.")
        return None, None

def main():
    finder = AdvancedBusRouteFinder()
    
    print_header()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            # Find routes between coordinates using ful l algorithm
            print("\n📍 ORIGIN LOCATION:")
            origin_lat, origin_lon = get_coordinates()
            if origin_lat is None:
                continue
                
            print("\n📍 DESTINATION LOCATION:")
            dest_lat, dest_lon = get_coordinates()
            if dest_lat is None:
                continue
            
            max_transfers = int(input("\nMax transfers allowed (0-3): ") or "2")
            max_walking = float(input("Max walking distance in meters (500-2000): ") or "1000")
            
            print("\n" + "="*50)
            print("🚀 RUNNING COMPLETE PATHFINDING ALGORITHM")
            print("="*50)
            
            journeys = finder.find_all_routes(
                origin_lat, origin_lon, dest_lat, dest_lon, 
                max_transfers, max_walking
            )
            
            print_detailed_journeys(journeys, finder)
        
        elif choice == "2":
            # Find routes between stops using full algorithm
            print("\n🚏 Available bus stops:")
            for stop_id, stop in finder.stops.items():
                print(f"  {stop_id}: {stop['stop_name']}")
            
            origin_id = input("\nEnter origin stop ID: ").strip().upper()
            dest_id = input("Enter destination stop ID: ").strip().upper()
            
            if origin_id not in finder.stops or dest_id not in finder.stops:
                print("❌ Invalid stop ID(s)!")
                continue
            
            if origin_id == dest_id:
                print("❌ Origin and destination cannot be the same!")
                continue
            
            max_transfers = int(input("Max transfers allowed (0-3): ") or "2")
            
            print("\n" + "="*50)
            print("🚀 RUNNING DIJKSTRA'S PATHFINDING ALGORITHM")
            print("="*50)
            
            # Use coordinates of the stops for the full algorithm
            origin_stop = finder.stops[origin_id]
            dest_stop = finder.stops[dest_id]
            
            journeys = finder.find_all_routes(
                origin_stop["latitude"], origin_stop["longitude"],
                dest_stop["latitude"], dest_stop["longitude"],
                max_transfers, 50  # Minimal walking since we're at exact stops
            )
            
            print_detailed_journeys(journeys, finder)
        
        elif choice == "3":
            # Search stops by name
            query = input("\n🔍 Enter bus stop name to search: ").strip()
            if query:
                results = finder.search_stops_by_name(query)
                if results:
                    print(f"\n🚏 Found {len(results)} stop(s):")
                    for stop in results:
                        print(f"  {stop['stop_id']}: {stop['stop_name']}")
                        print(f"    📍 {stop['address']}")
                else:
                    print("❌ No stops found!")
        
        elif choice == "4":
            # Show all bus stops
            print("\n🚏 All bus stops:")
            for stop_id, stop in finder.stops.items():
                print(f"  {stop_id}: {stop['stop_name']}")
                print(f"    📍 {stop['address']}")
                print(f"    🚌 Routes: {len(finder.stop_routes.get(stop_id, []))}")
                print()
        
        elif choice == "5":
            print("\n👋 Thank you for using Advanced Bus Route Finder!")
            break
        
        else:
            print("❌ Invalid choice! Please select 1-5.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()