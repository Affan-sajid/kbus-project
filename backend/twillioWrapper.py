from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()


class WabaApi ():
    def __init__(self):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")

        auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        self.fromnumber = "+14155238886"
        self.client = Client(account_sid, auth_token)

    def send_template(self,to_number,templateid,variable=None):
        message = self.client.messages.create(
        from_=f'whatsapp:{self.fromnumber}',
        content_sid= templateid,
        content_variables= variable,
        to=f'whatsapp:+91{to_number}')
        return message.sid
    def send_message(self,to_number,message):
        message = self.client.messages.create(
        from_=f'whatsapp:{self.fromnumber}',
        body=message,
        to=f'whatsapp:+91{to_number}'
        )

        return message.sid
    
if __name__ == '__main__':
    Wa = WabaApi()
    # print(Wa.send_template('8089438821',"HXb5b62575e6e4ff6129ad7c8efe1f983e",'{"1":"12/1","2":"3pm"}'))
    print(Wa.send_message('8089438821','hello this is a test message'))

       