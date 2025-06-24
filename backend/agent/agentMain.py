import os
import requests
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal, Optional
import dotenv

dotenv.load_dotenv()

# Setup OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gmap_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Structured schema

# --------------------------------------------------
# get address
# --------------------------------------------------


class AgentResponse(BaseModel):
    status: Literal["need_more_info", "place_normalized"]
    question: Optional[str] = None
    place: Optional[str] = None
    confidence: Optional[Literal["high", "medium", "low"]] = None
    next_action: Optional[str] = None

system_prompt = """
You are a location resolution assistant helping users plan trips.
Your job is to determine if the user has provided a valid, unambiguous place name.

Return JSON in one of two formats:

1. If unclear:
{
  "status": "need_more_info",
  "question": "Could you clarify? Do you mean Palath in Kozhikode?",
  "next_action": "call_tool:get_input"
}

2. If resolved:
{
  "status": "place_normalized",
  "place": "Palath, Kakkodi, Kozhikode, Kerala, India",
  "confidence": "high",
  "next_action": "call_tool:get_coordinates"
}

Only respond with one of these JSON formats. Do not explain.
"""

def call_agent(messages):
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        response_format=AgentResponse,
    )
    return response.choices[0].message.parsed

def resolve_place_interactively():
    user_input = input("User: ")
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}]
    
    parsed = call_agent(messages)

    while parsed.status == "need_more_info":
        print("Bot:", parsed.question)
        user_reply = input("User: ")
        messages.append({"role": "assistant", "content": parsed.question})
        messages.append({"role": "user", "content": user_reply})
        parsed = call_agent(messages)

    return parsed, messages

def get_coordinates(place):
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": place, "key": gmap_api_key}
    response = requests.get(endpoint, params=params)
    return response.json()

def confirm_location_loop(parsed, messages):
    while True:
        geo_data = get_coordinates(parsed.place)
        print(geo_data)

        if geo_data["status"] != "OK":
            print("❌ Error getting location. Please try again.")
            return None

        location = geo_data["results"][0]["geometry"]["location"]
        address = geo_data["results"][0]["formatted_address"]
        print(f"\nTEMPLATE‼️ with image of dropped loc \n📍 I found this location: \nAddress: {address}\nCoordinates: {location['lat']}, {location['lng']}")
      

        confirm = input("\nTEMPLATE‼️ Do you want to proceed with this location? (yes/no): ").strip().lower()

        if confirm in ["yes", "y"]:
            return {
                "place": address,
                "lat": location["lat"],
                "lng": location["lng"]
            }
        else:
            # Let LLM handle what to ask next
            follow_prompt = f"The user rejected the location '{address}'. What follow-up question should I ask to clarify the input further?"
            messages.append({"role": "assistant", "content": f"The user rejected '{address}'."})
            messages.append({"role": "user", "content": "Let's try that again."})

            parsed = call_agent(messages)

            while parsed.status == "need_more_info":
                print("Bot:", parsed.question)
                user_reply = input("User: ")
                messages.append({"role": "assistant", "content": parsed.question})
                messages.append({"role": "user", "content": user_reply})
                parsed = call_agent(messages)



def getaddress():
    parsed, messages = resolve_place_interactively()
    result = confirm_location_loop(parsed, messages)
    return result


user = {
    "user_id": None,
    "to": None,
    "current": None,
    'stage': 'new'
    }


   


# -----------------------------
# Main Flow
# -----------------------------
print('TEMPLATE‼️ hello there welcome to busbot whwre do you want to go?')

result = getaddress()
if result:
    print("\n✅ Finalized Location:")
    to_addres = result
    user['to'] = to_addres
    user['stage'] = "recived_to"

else:
    print("⚠️ Could not resolve the location.")




print(
    "\nTEMPLATE‼️ 🗺️ Great! Now, where are you starting from?\n"
    "Please choose one of the following:\n"
    "1. Type your current address\n"
    "2. Paste a Google Maps link\n"
    "3. Type 'send current location' "
)

user_input = input("User: ").strip()

if user_input.lower() == "send current location" or user_input.lower() == "s":
    # Use hardcoded landmark for demo
    current_address = "Landmark World, Calicut, Kerala, India"
    print(f"\nUsing test location: {current_address}")
    

# elif "https://maps.google.com" in user_input or "goo.gl/maps" in user_input:
#     # Attempt to extract the place from Google Maps URL
#     print("TEMPLATE‼️ 📎 You sent a Google Maps link. Trying to resolve...")
#     messages = [{"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_input}]
#     parsed = call_agent(messages)
#     confirmed = confirm_location_loop(parsed, messages)
#     user["current"] = confirmed

else:
    # Treat input as free text
    print("TEMPLATE‼️ 📍 Resolving typed address...")
    current_address = getaddress()
    
user["current"] = current_address
user["stage"] = "received_current"

print("\n✅ Final Status:")
print("🚌 Destination:", user["to"]["place"])
print("📍 Current Location:", user["current"])

# if input("user: ") == ' send current location':
#     currentloc = 'landmark world calicut kerala india '
# elif if include map link 
# else call gett to_addres



