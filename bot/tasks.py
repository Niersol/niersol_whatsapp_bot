import requests
from openai import OpenAI
from django.conf import settings
from celery import shared_task
from asgiref.sync import sync_to_async
from .models import Conversation
import logging

logger = logging.getLogger(__name__)

# Instantiate your OpenAI client with the API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# WhatsApp Cloud API details
WHATSAPP_CLOUD_API_BASE = "https://graph.facebook.com/v21.0"  # Update to the version you are using
PHONE_NUMBER_ID = "507892592398007"
WHATSAPP_TOKEN = settings.WHATSAPP_TOKEN

def send_whatsapp_message(to_number, message_text):
    """
    Send a WhatsApp message via the WhatsApp Cloud API.
    """
    logger.info("[send_whatsapp_message] Called with:")
    logger.info(f"  to_number = {to_number}")
    logger.info(f"  message_text = {message_text}")

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

    logger.info("[send_whatsapp_message] POSTing to WhatsApp Cloud API:")
    logger.info(f"  URL = {url}")
    logger.info(f"  Headers = {headers}")
    logger.info(f"  JSON Body = {data}")

    response = requests.post(url, headers=headers, json=data)
    logger.info(f"[send_whatsapp_message] Response status code = {response.status_code}")
    logger.info(f"[send_whatsapp_message] Response text = {response.text}")

    # Raise an error if the request failed
    response.raise_for_status()

    return response.json()

@shared_task
def process_incoming_message(sender_phone, thread_id):
    """
    Retrieves conversation info from OpenAI, sends a WhatsApp message with the assistant response.
    """
    logger.info("[process_incoming_message] Task started")
    logger.info(f"  sender_phone = {sender_phone}")
    logger.info(f"  thread_id = {thread_id}")

    # Debug: check the OpenAI API key is loaded
    logger.info(f"[process_incoming_message] Using OpenAI API key: {settings.OPENAI_API_KEY}")

    # Attempt to create and poll a run on the given thread
    try:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id='asst_bUcnaEiCLHPcFv1TDr4GfzVu'
        )
    except Exception as e:
        logger.info(e)
        return  # or re-raise, depending on your error handling

    if run.status == 'completed':
        try:
            messages = client.beta.threads.messages.list(thread_id=thread_id)

            # Cautiously check if messages.data is not empty
            if messages.data:
                # Adjust indexing if needed based on actual response structure
                assistant_response = messages.data[0].content[0].text.value

                # Send the response back on WhatsApp
                send_whatsapp_message(sender_phone, assistant_response)
            else:
                logger.info("[process_incoming_message] No messages returned by OpenAI.")
        except Exception as e:
            logger.info("[process_incoming_message] ERROR fetching messages or sending WhatsApp message")
            logger.info(e)
    else:
        logger.info(f"[process_incoming_message] run status is not 'completed': {run.status}")

@shared_task
def simple_task():
    return "Task completed!"