from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import requests
import logging

# ————————————————————————————————————————————————————————————————————————
# Configuration & Logging
# ————————————————————————————————————————————————————————————————————————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o"

# ————————————————————————————————————————————————————————————————————————
# Data models for function arguments and responses
# ————————————————————————————————————————————————————————————————————————
class NormalizePlaceArgs(BaseModel):
    raw: str = Field(..., description="User‑provided place input")

class NormalizePlaceResult(BaseModel):
    place: str = Field(..., description="Fully qualified address")
    confidence: str = Field(..., description="low|medium|high")

class GeocodePlaceArgs(BaseModel):
    place: str = Field(..., description="Normalized address to geocode")

class GeocodePlaceResult(BaseModel):
    lat: float
    lng: float
    address: str = Field(..., description="Formatted address from Google")

# ————————————————————————————————————————————————————————————————————————
# Tool implementations
# ————————————————————————————————————————————————————————————————————————
def normalize_place(raw: str) -> NormalizePlaceResult:
    """
    Use an LLM call to normalize the raw place into a full address.
    """
    logger.info(f"Normalizing place: {raw!r}")
    system_prompt = (
        "You are a location normalization assistant.\n"
        "Input: a user‑provided place string. Output JSON with keys "
        "'place' (full address) and 'confidence' (low|medium|high)."
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": raw}
        ],
        tools=[],
        function_call=None,
        response_format=NormalizePlaceResult,
    )
    result = resp.choices[0].message.parsed
    logger.info(f"Normalized to {result.place!r} (confidence={result.confidence})")
    return result

def geocode_place(place: str) -> GeocodePlaceResult:
    """
    Call Google Maps Geocoding API to return lat/lng and formatted address.
    """
    logger.info(f"Geocoding place: {place!r}")
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": place, "key": GOOGLE_MAPS_API_KEY}
    resp = requests.get(url, params=params).json()
    status = resp.get("status")
    if status != "OK" or not resp.get("results"):
        raise RuntimeError(f"Geocoding failed: {status}")
    first = resp["results"][0]
    loc = first["geometry"]["location"]
    formatted = first["formatted_address"]
    logger.info(f"Geocoded to ({loc['lat']}, {loc['lng']}) → {formatted!r}")
    return GeocodePlaceResult(lat=loc["lat"], lng=loc["lng"], address=formatted)

# ————————————————————————————————————————————————————————————————————————
# Tool metadata for OpenAI function‑calling
# ————————————————————————————————————————————————————————————————————————
normalize_tool = {
    "name": "normalize_place",
    "description": "Normalize a user‑provided place string to a full address and confidence level",
    "parameters": NormalizePlaceArgs.schema(),
}

geocode_tool = {
    "name": "geocode_place",
    "description": "Convert a normalized address into latitude, longitude, and formatted address",
    "parameters": GeocodePlaceArgs.schema(),
}

# ————————————————————————————————————————————————————————————————————————
# Main interactive loop
# ————————————————————————————————————————————————————————————————————————
def main():
    print("🚏 Welcome to PlaceBot! Where would you like to go?")
    user_input = input("You: ").strip()

    # 1) Ask model to normalize, then optionally geocode
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You help normalize and geocode places."},
            {"role": "user",   "content": user_input},
        ],
        tools=[normalize_tool, geocode_tool],
        function_call="auto",
    )
    msg = response.choices[0].message

    # 2) Dispatch normalize_place if called
    if msg.function_call and msg.function_call.name == "normalize_place":
        args = NormalizePlaceArgs.parse_obj(msg.function_call.arguments)
        norm = normalize_place(**args.model_dump())
        # feed the normalization result back
        followup = client.chat.completions.create(
            model=MODEL,
            messages=[
                *response.usage.messages,
                {
                    "role": "function",
                    "name": "normalize_place",
                    "content": norm.json()
                }
            ],
            tools=[normalize_tool, geocode_tool],
            function_call="auto",
        )
        msg = followup.choices[0].message

    # 3) Dispatch geocode_place if called
    if msg.function_call and msg.function_call.name == "geocode_place":
        args = GeocodePlaceArgs.parse_obj(msg.function_call.arguments)
        geo = geocode_place(**args.model_dump())
        # final confirmation
        print(f"\n✅ Location found!\n"
              f"Address: {geo.address}\n"
              f"Coordinates: {geo.lat}, {geo.lng}")
    else:
        # if no tool called, just print the assistant's reply
        print("\n" + (msg.content or "").strip())

if __name__ == "__main__":
    main()
