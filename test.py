import requests




key = "5c4fc36edcfb499f8695360c8c9282ec"

def search (name):
# name = "Pala KSRTC Bus Stand, Kottayam, Kerala, India"

    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": name,
        "key": key,  # Replace with your actual OpenCage API key
        "countrycode": "in",    # Optional: limit to France
        "limit": 1              # Optional: return only 1 best result
    }

    res = requests.get(url, params=params)
    data = res.json()

    print(data)
    print(data["results"])

    if data["results"]:
        top = data["results"][0]
        lat = top["geometry"]["lat"]
        lon = top["geometry"]["lng"]
        formatted = top["formatted"]
        confidence = top["confidence"]
        componetnts = top["components"]

        print(lat, lon, formatted, confidence , componetnts)


