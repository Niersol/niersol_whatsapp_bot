import requests
from openai import OpenAI
from django.conf import settings
from celery import shared_task
from asgiref.sync import sync_to_async
from .models import Conversation,Business
import logging
import random
import time
from .utils import send_whatsapp_message,get_gpt_response
logger = logging.getLogger(__name__)


# WhatsApp Cloud API details


@shared_task
def send_message_whatsapp(sender_phone,phone_number_id,thread_id):
    conversation = Conversation.objects.get(phone_number=sender_phone)
    business = Business.objects.get(phone_id=phone_number_id)
    time.sleep(random.uniform(10, 15))
    response = get_gpt_response(thread_id,business.assistant_id)
    send_whatsapp_message(sender_phone,phone_number_id,response)
    conversation.is_active = False
    conversation.save()
    return