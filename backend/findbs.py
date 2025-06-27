
importjson
 from errno import ERFKILL, WSAEBADF
import heapq
from tkinter import E, W
from typing import ForwardRef

from flask.cli import F
import mathimport heapq#!/usr/bin/env python3




















# from ast import Break
# import operator
# from tracemalloc import stop
# from turtle import pensize
# from dataclasses import dataclass , field


# SAMPLE_DATA = {
#     "bus_stops": [
#         {
#             "stop_id": "BS001",
#             "stop_name": "Central Station",
#             "latitude": 11.2588,
#             "longitude": 75.7804,
#             "address": "Central Station Rd, Kozhikode"
#         },
#         {
#             "stop_id": "BS002", 
#             "stop_name": "Medical College",
#             "latitude": 11.2496,
#             "longitude": 75.7666,
#             "address": "Medical College Rd, Kozhikode"
#         },
#         {
#             "stop_id": "BS003",
#             "stop_name": "Palayam Market",
#             "latitude": 11.2588,
#             "longitude": 75.7714,
#             "address": "Palayam, Kozhikode"
#         },
#         {
#             "stop_id": "BS004",
#             "stop_name": "Beach Road",
#             "latitude": 11.2750,
#             "longitude": 75.7747,
#             "address": "Beach Rd, Kozhikode"
#         },
#         {
#             "stop_id": "BS005",
#             "stop_name": "University",
#             "latitude": 11.1271,
#             "longitude": 75.8449,
#             "address": "Calicut University, Malappuram"
#         },
#         {
#             "stop_id": "BS006",
#             "stop_name": "Airport Junction",
#             "latitude": 11.1410,
#             "longitude": 75.9550,
#             "address": "Airport Rd, Kozhikode"
#         },
#         {
#             "stop_id": "BS007",
#             "stop_name": "Private Bus Stand",
#             "latitude": 11.2480,
#             "longitude": 75.7763,
#             "address": "Mavoor Rd, Kozhikode"
#         },
#         {
#             "stop_id": "BS008",
#             "stop_name": "KSRTC Bus Stand",
#             "latitude": 11.2447,
#             "longitude": 75.7730,
#             "address": "Mavoor Rd, Kozhikode"
#         }
#     ],
#     "bus_routes": [
#         {
#             "route_id": "R001",
#             "route_number": "1A",
#             "route_name": "Central Station - Airport",
#             "stops": ["BS001", "BS003", "BS002", "BS005", "BS006"],
#             "operator": "KSRTC",
#             "route_type": "ordinary",
#             "frequency_minutes": 30
#         },
#         {
#             "route_id": "R002", 
#             "route_number": "1B",
#             "route_name": "Airport - Central Station",
#             "stops": ["BS006", "BS005", "BS002", "BS003", "BS001"],
#             "operator": "KSRTC",
#             "route_type": "ordinary",
#             "frequency_minutes": 30
#         },
#         {
#             "route_id": "R003",
#             "route_number": "2",
#             "route_name": "Beach Road Circular",
#             "stops": ["BS001", "BS004", "BS003", "BS007", "BS008", "BS001"],
#             "operator": "Private",
#             "route_type": "ordinary",
#             "frequency_minutes": 20
#         },
#         {
#             "route_id": "R004",
#             "route_number": "5E",
#             "route_name": "Express - Central to University",
#             "stops": ["BS001", "BS002", "BS005"],
#             "operator": "KSRTC",
#             "route_type": "express",
#             "frequency_minutes": 60
#         },
#         {
#             "route_id": "R005",
#             "route_number": "5E-R",
#             "route_name": "Express - University to Central",
#             "stops": ["BS005", "BS002", "BS001"],
#             "operator": "KSRTC",
#             "route_type": "express",
#             "frequency_minutes": 60
#         },
#         {
#             "route_id": "R006",
#             "route_number": "3",
#             "route_name": "Medical College - Beach Road",
#             "stops": ["BS002", "BS003", "BS004"],
#             "operator": "Private",
#             "route_type": "ordinary",
#             "frequency_minutes": 45
#         }
#     ]
# }

# @dataclass
# class RouteSegment:
#     """Represents one segment of a journey(single bus ride )"""
#     route_id: str 
#     route_number: str 
#     route_name: str 
#     operator: str 
#     from_stop_id:str 
#     to_stop_id:str 
#     from_stop_name: str 
#     to_stop_name : str 
#     duration_minutes: int 
#     stops_count: int 
#     fare : float 
#     route_types: str 


# #
# # ---- init----
# stops = {}
# routes = {}
# stop_routes = {}

# # ---- load data ----
# for stop_data in SAMPLE_DATA["bus_stops"]:
#     stops[stop_data["stop_id"]] = stop_data


# for route_data in SAMPLE_DATA["bus_routes"]:
#     routes[route_data["route_id"]] = route_data

#     for stop_id in route_data["stops"]:
#         if stop_id not in stop_routes:
#             stop_routes[stop_id] = []
#         stop_routes[stop_id].append(route_data["route_id"])

# # ---- build route graph ----
# route_graph={}
# for stop_idmain in stops.keys():
#     route_graph[stop_idmain] = []
#     print(stop_idmain)

# #   all routes passing thoruh this stop
#     for route_id in stop_routes.get(stop_idmain,[]):
#         route = routes[route_id]
#         # print(route)

#         for stop_id in route["stops"]:
#             current_idx = route["stops"].index(stop_id)
#             # print(current_idx)

#             for target_idx in range(current_idx+1, len(route["stops"])):
#                 target_stop = route["stops"][target_idx]

#                 if target_stop == stop_id:
#                     continue
#                 print(f"stop_id:{stop_idmain} route_id:{route_id} stop_idreachble:{stop_id} indexofstop:{current_idx} targetidx:{target_idx} target_stop:{target_stop}")

#                 duration = self.calculate_segment_duration(route_id, current_idx)
#                 fare = self. calculate_segment_fare(route_id,current_idx, target_idx)
                
#                 segment = RouteSegment(
#                       route_id: str 
#                     route_number: str 
#                     route_name: str 
#                     operator: str 
#                     from_stop_id:str 
#                     to_stop_id:str 
#                     from_stop_name: str 
#                     to_stop_name : str 
#                     duration_minutes: int 
#                     stops_count: int 
#                     fare : float 
#                     route_types: str 
#                 )
#             # route -  routes
#     print()
#     break
# print(routes)
# print(stops)


WSAEBADFF
QEF
W



ERFKILLFE
ForwardRefEF
E
ForwardRefEFF
E
FEFEFEFEFEFEFEpython3
