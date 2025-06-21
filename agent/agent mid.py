import os

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




# --------------------------------------------------------------
# Step 1: Define the response format in a Pydantic model
# --------------------------------------------------------------

user = {
    "user_id": None,
    "name": None,
    "to": None,
    "current": None,
    "to_cordn": None,
    "current_cordn": None 
    }




class CalendarEvent(BaseModel):
    toplace: str = Field(
        description="the place that the user needs to go"
    )
    to_longitude: str = Field(
        description="longtitude of the place that user needs to go"
    )
    to_latitude: str = Field(
        description="latitude of the place that the user needs to go"
    )
 


# --------------------------------------------------------------
# Step 2: Call the model
# --------------------------------------------------------------

completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    response_format=CalendarEvent,
)

print(completion)
# --------------------------------------------------------------
# Step 3: Parse the response
# --------------------------------------------------------------

event = completion.choices[0].message.parsed
print(event.name)
print(event.date)
print(event.participants)
