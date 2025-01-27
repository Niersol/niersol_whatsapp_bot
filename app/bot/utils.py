import openai
from django.conf import settings
import time
import requests
from .models import Conversation
import json
from openai import OpenAI 
client = OpenAI(api_key=settings.OPENAI_API_KEY)
def get_gpt_response(thread_id):
    """
    Sends user_message to GPT and returns the response.
    """
    try:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id='asst_Uw3un2NZHQm0McEVdTJgN6sw'
        )
        if run.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread_id)

                # Cautiously check if messages.data is not empty
                if messages.data:
                    # Adjust indexing if needed based on actual response structure
                    assistant_response = messages.data[0].content[0].text.value
                    return assistant_response
                    # Send the response back on WhatsApp
                else:
                     return "No message Data Found"
                
        else:
             return "run not completed"
        # response = client.chat.completions.create(
        #     model="gpt-4o",  # or "gpt-4", etc.
        #     messages=[
        #         {"role": "system", "content": "You are a helpful WhatsApp chatbot."},
        #         {"role": "user", "content": user_message},
        #     ],
        # )
        # answer = response.choices[0].message.content
        # return answer.strip()
    except Exception as e:
        print(f"client API error: {str(e)}")
        return "Sorry, I couldn't process that at the moment."


WHATSAPP_CLOUD_API_BASE = "https://graph.facebook.com/v21.0"  # Update to the version you are using
PHONE_NUMBER_ID = "507892592398007"
WHATSAPP_TOKEN = settings.WHATSAPP_TOKEN


def send_whatsapp_message(to_number, message_text):

    url = f"{WHATSAPP_CLOUD_API_BASE}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "text": {
            "body": message_text
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def mark_message_as_seen(message_id):
    """
    Marks the incoming WhatsApp message as read.
    """
    url = f"{WHATSAPP_CLOUD_API_BASE}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Mark as read response code: {response.status_code}")
    print(f"Mark as read response body: {response.text}")