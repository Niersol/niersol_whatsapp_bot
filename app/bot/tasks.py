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


@shared_task
def simple_task():
    return "Task completed!"