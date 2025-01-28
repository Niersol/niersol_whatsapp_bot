import requests
from openai import OpenAI
from django.conf import settings
from celery import shared_task
from asgiref.sync import sync_to_async
from .models import Conversation
import logging
import random
import time
from .utils import send_whatsapp_message,get_gpt_response
logger = logging.getLogger(__name__)

# Instantiate your OpenAI client with the API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# WhatsApp Cloud API details


@shared_task
def send_message_whatsapp(sender_phone,thread_id):
    conversation = Conversation.objects.get(phone_number=sender_phone)
    time.sleep(random.uniform(4, 10))
    response = get_gpt_response(thread_id)
    send_whatsapp_message(sender_phone,response)
    conversation.is_active = False
    conversation.save()
    return