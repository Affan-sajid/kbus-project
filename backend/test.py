import os
import requests
import dotenv

dotenv.load_dotenv()

# def get_coordina÷tes(place: str):
place = "Kizhmuri, Omanoor, Kerala, India"
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
params = {"address": place, "key": api_key}

response = requests.get(endpoint, params=params)
data = response.json()

if data["status"] == "OK":
    location = data["results"][0]["geometry"]["location"]
    print(location["lat"])
    print(location["lng"],)
    print(data["results"][0]["formatted_address"])
    






























# import requests




# key = "5c4fc36edcfb499f8695360c8c9282ec"

# def search (name):
# # name = "Pala KSRTC Bus Stand, Kottayam, Kerala, India"

#     url = "https://api.opencagedata.com/geocode/v1/json"
#     params = {
#         "q": name,
#         "key": key,  # Replace with your actual OpenCage API key
#         "countrycode": "in",    # Optional: limit to France
#         "limit": 1              # Optional: return only 1 best result
#     }

#     res = requests.get(url, params=params)
#     data = res.json()

#     print(data)
#     print(data["results"])

#     if data["results"]:
#         top = data["results"][0]
#         lat = top["geometry"]["lat"]
#         lon = top["geometry"]["lng"]
#         formatted = top["formatted"]
#         confidence = top["confidence"]
#         componetnts = top["components"]

#         print(lat, lon, formatted, confidence , componetnts)


# search('Kizhumuri, Omanoor, Kerala, India')