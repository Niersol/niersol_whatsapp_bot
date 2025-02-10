import json
import logging
import traceback
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
import jwt
from .utils import get_gpt_response, send_whatsapp_message, mark_message_as_seen,get_media_url,download_media,download_audio,translate_audio
from .models import Conversation,Business
from .tasks import send_message_whatsapp
from openai import OpenAI
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import os
# Initialize Logger
logger = logging.getLogger("app_logger")

client = OpenAI(api_key=settings.OPENAI_API_KEY)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


@csrf_exempt
def whatsapp_webhook(request):
    logger.info("Received request to whatsapp_webhook")
    logger.debug(f"Request method: {request.method}")

    if request.method == "GET":
        verify_token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if verify_token == VERIFY_TOKEN:
            logger.info("WhatsApp webhook verification successful")
            return HttpResponse(challenge, status=200)
        else:
            logger.warning("WhatsApp webhook verification failed")
            return HttpResponse("Verification token mismatch", status=403)

    elif request.method == "POST":
        try:
            incoming_data = json.loads(request.body.decode("utf-8"))
            logger.debug(f"Incoming JSON data: {incoming_data}")

            if "entry" not in incoming_data:
                logger.warning("Invalid WhatsApp webhook payload (no 'entry' field)")
                return HttpResponse("No 'entry' in payload", status=200)

            for entry in incoming_data.get("entry", []):
                logger.debug(f"Processing entry: {entry}")

                for change in entry.get("changes", []):
                    logger.debug(f"Processing change: {change}")

                    value = change.get("value", {})
                    phone_number_id = value.get("metadata", {}).get("phone_number_id")  # Extract phone_number_id
                    messages = value.get("messages", [])

                    for msg in messages:
                        sender_phone = msg.get("from")
                        message_id = msg.get("id")
                        if sender_phone:
                            try:
                                business = Business.objects.get(phone_id=phone_number_id)
                            except Exception as e:
                                print("business phone number not registered")
                                return HttpResponse("Event received", status=200)
                            conversation, created = Conversation.objects.get_or_create(
                                business=business,
                                phone_number=sender_phone
                            )
                            if created:
                                try:
                                    thread = client.beta.threads.create()
                                    conversation.thread_id = thread.id
                                    conversation.save()
                                    logger.info(f"New thread created: {thread.id}")
                                except Exception as e:
                                    logger.error(f"Error creating OpenAI thread: {e}")
                                    traceback.print_exc()
                                    continue
                            thread_id = conversation.thread_id

                            mark_message_as_seen(message_id,phone_number_id)
                        if conversation.is_active:
                            if "text" in msg:
                                user_text = msg.get("text", {}).get("body", "")
                                client.beta.threads.messages.create(
                                    thread_id=thread_id, role="user", content=user_text
                                )
                            elif "image" in msg:
                                caption = msg["image"].get("caption", "")
                                media_id = msg["image"]["id"]
                                media_url = get_media_url(media_id)
                                file_id = download_media(media_url,media_id)



                                if caption:
                                    client.beta.threads.messages.create(
                                        thread_id=thread_id,role="user",content=[
                                            {
                                                "type":"text",
                                                "text":caption
                                            },{
                                                "type":"image_file",
                                                "image_file":{
                                                    "file_id":file_id,
                                                    "detail":"auto"
                                                }
                                            }
                                        ]
                                    )
                                else:
                                    client.beta.threads.messages.create(
                                        thread_id=thread_id,role="user",content=[
                                            {
                                                "type":"image_file",
                                                "image_file":{
                                                    "file_id":file_id,
                                                    "detail":"auto"
                                                }
                                            }
                                        ]
                                    )
                            elif "audio" in msg:
                                audio_id = msg['audio']['id']
                                audio_url = get_media_url(audio_id)
                                file_path = download_audio(audio_url,audio_id)
                                translation= translate_audio(file_path)
                                client.beta.threads.messages.create(
                                    thread_id=thread_id, role="user", content=translation
                                )

                        else:
                            if "text" in msg:
                                user_text = msg.get("text", {}).get("body", "")
                                client.beta.threads.messages.create(
                                    thread_id=thread_id, role="user", content=user_text
                                )
                            elif "image" in msg:
                                caption = msg["image"].get("caption", "")
                                media_id = msg["image"]["id"]
                                media_url = get_media_url(media_id)
                                file_id = download_media(media_url,media_id)


                                if caption:
                                    client.beta.threads.messages.create(
                                        thread_id=thread_id,role="user",content=[
                                            {
                                                "type":"text",
                                                "text":caption
                                            },{
                                                "type":"image_file",
                                                "image_file":{
                                                    "file_id":file_id,
                                                    "detail":"auto"
                                                }
                                            }
                                        ]
                                    )
                                else:
                                    client.beta.threads.messages.create(
                                        thread_id=thread_id,role="user",content=[
                                            {
                                                "type":"image_file",
                                                "image_file":{
                                                    "file_id":file_id,
                                                    "detail":"auto"
                                                }
                                            }
                                        ]
                                    )
                            elif "audio" in msg:
                                audio_id = msg['audio']['id']
                                audio_url = get_media_url(audio_id)
                                file_path = download_audio(audio_url,audio_id)
                                translation= translate_audio(file_path)
                                client.beta.threads.messages.create(
                                    thread_id=thread_id, role="user", content=translation
                                )

                            conversation.is_active = True
                            conversation.save()

                            send_message_whatsapp.delay(sender_phone,phone_number_id, thread_id)

            return HttpResponse("Event received", status=200)

        except Exception as e:
            logger.exception(f"Error processing WhatsApp webhook: {e}")
            traceback.print_exc()
            return HttpResponse("Internal Server Error", status=500)

    logger.warning("Invalid request method for WhatsApp webhook")
    return HttpResponse("Invalid request", status=404)


def privacy_policy(request):
    return render(request, "index.html")
