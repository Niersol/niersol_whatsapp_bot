from django.conf import settings
import time
import requests
from .models import Conversation
import json
import os
import mimetypes
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from openai import OpenAI 
import io
mimetypes.add_type('audio/ogg', '.ogg')
mimetypes.add_type('audio/mp4', '.m4a')
mimetypes.add_type('audio/amr', '.amr')
mimetypes.add_type('audio/aac', '.aac')
mimetypes.add_type('audio/mp3', '.mp3')

client = OpenAI(api_key=settings.OPENAI_API_KEY)
WHATSAPP_CLOUD_API_BASE = "https://graph.facebook.com/v21.0"  # Update to the version you are using
WHATSAPP_TOKEN=os.getenv("WHATSAPP_APP_SECRET")
import logging
logger = logging.getLogger("app_logger")

def get_gpt_response(thread_id,assistant_id):
    """
    Sends user_message to GPT and returns the response.
    """
    try:
        
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        logger.info(run)
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
    except Exception as e:
        logger.info(f"client API error: {str(e)}")
        return "Sorry, I am unavailable at the moment, can you please contact later?"

def send_whatsapp_message(to_number,from_number, message_text):

    url = f"{WHATSAPP_CLOUD_API_BASE}/{from_number}/messages"
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


def mark_message_as_seen(message_id,from_number):
    """
    Marks the incoming WhatsApp message as read.
    """
    url = f"{WHATSAPP_CLOUD_API_BASE}/{from_number}/messages"
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


def get_media_url(media_id):
    """Fetches the media URL using the media ID."""
    url = f"{WHATSAPP_CLOUD_API_BASE}/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("url")
    else:
        logger.error(f"Failed to fetch media URL for {media_id}")
        return None
    

def download_audio(audio_url,audio_id):
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    response = requests.get(audio_url, headers=headers)

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        logger.info(content_type)
        extension = mimetypes.guess_extension(content_type) or ".bin"
        logger.info(extension)
        # Generate file path for Django's default storage
        file_name = f"{audio_id}{extension}"
        logger.info(file_name)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        saved_path = default_storage.save(file_path, ContentFile(response.content))
        return saved_path
    else:
        logger.error(f"Failed to download media from {audio_url}")
        return None
    
def translate_audio(file_path):
    try:
        # Open the saved file in binary mode
        with default_storage.open(file_path, "rb") as file:
            file_content = file.read()  # Read file into bytes
            
            # Convert to BytesIO object
            file_stream = io.BytesIO(file_content)
            file_stream.name = file_path  # Set a name for OpenAI reference

            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=file_stream,
                response_format="text"
            )
            logger.info(transcription)
            return transcription
    except Exception as e:
        logger.error(f"Error uploading file to OpenAI: {e}")
        return None
    
def download_media(media_url, media_id):
    """Downloads media from the given URL, saves it using Django storage, and uploads to OpenAI."""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    response = requests.get(media_url, headers=headers)

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        extension = mimetypes.guess_extension(content_type) or ".bin"

        # Generate file path for Django's default storage
        file_name = f"{media_id}{extension}"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Save the file using Django's storage system
        saved_path = default_storage.save(file_path, ContentFile(response.content))

        # Open the saved file and upload it to OpenAI
        openai_file_id = upload_file_to_openai(saved_path)

        return openai_file_id
    else:
        logger.error(f"Failed to download media from {media_url}")
        return None

def upload_file_to_openai(file_path):
    """Uploads the file stored in Django's default storage to OpenAI."""
    try:
        # Open the saved file in binary mode
        with default_storage.open(file_path, "rb") as file:
            file_content = file.read()  # Read file into bytes
            
            # Convert to BytesIO object
            file_stream = io.BytesIO(file_content)
            file_stream.name = file_path  # Set a name for OpenAI reference

            # Upload to OpenAI
            openai_file = client.files.create(file=file_stream, purpose="vision")

        logger.info(f"File uploaded to OpenAI: {openai_file.id}")
        return openai_file.id  # Return OpenAI file ID for later use
    except Exception as e:
        logger.error(f"Error uploading file to OpenAI: {e}")
        return None