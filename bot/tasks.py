import requests
from openai import OpenAI
from django.conf import settings
from celery import shared_task
from asgiref.sync import sync_to_async
from .models import Conversation
client = OpenAI(api_key=settings.OPENAI_API_KEY)

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


@shared_task
def process_incoming_message(sender_phone,thread_id):

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id='asst_bUcnaEiCLHPcFv1TDr4GfzVu'
    )
    
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
        thread_id=thread_id
        )
        assistant_response = messages.data[0].content[0].text.value
        send_whatsapp_message(sender_phone,assistant_response)

    else:
        print(run.status)