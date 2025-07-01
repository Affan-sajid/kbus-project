from flask import Flask,  request 
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)

user_state = {}




@app.route("/Whatsapp", methods=['POST'])
def whatsapp_webhook():
    print(request)
    incoming_msg = request.values.get('Body','').strip()
    from_number = request.values.get('From','')
    latitude = request.form.get('Latitude')
    longitude = request.form.get('Longitude')
    print(f'message from {from_number}: {incoming_msg}')

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg : 
        user_state[from_number] = {'step':'awaiting_destination'}
        msg.body("👋 Welcome! Please type your destination or share a pin 📍.")
        return str(resp)

    if user_state.get(from_number, {}).get('step') == 'awaiting_destination':
        if latitude and longitude:
            # If shared pin
            user_state[from_number] = {
                'step': 'awaiting_current_location',
                'destination_coords': (latitude, longitude)
            }
        msg.body(f"📍 Destination received! Now, please share your current location. {latitude}, {longitude}")

    else:
        # Assume typed destination
        user_state[from_number] = {
            'step': 'awaiting_current_location',
            'destination': incoming_msg.strip().title()
        }
        msg.body(f"📍 Destination '{incoming_msg}' noted! Now, please share your current location.")
    return str(resp)

app.run(port=8000, debug=True)