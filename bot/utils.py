import openai
from django.conf import settings
from openai import OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)
def get_gpt_response(user_message):
    """
    Sends user_message to GPT and returns the response.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4", etc.
            messages=[
                {"role": "system", "content": "You are a helpful WhatsApp chatbot."},
                {"role": "user", "content": user_message},
            ],
        )
        answer = response.choices[0].message.content
        return answer.strip()
    except Exception as e:
        print(f"client API error: {str(e)}")
        return "Sorry, I couldn't process that at the moment."

import requests

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
