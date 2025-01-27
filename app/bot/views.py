import json
import traceback
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from asgiref.sync import sync_to_async

from .utils import get_gpt_response, send_whatsapp_message
from .models import Conversation
from .tasks import process_incoming_message
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

VERIFY_TOKEN = "03248673732"  # same token you set in Meta Dashboard

@csrf_exempt
def whatsapp_webhook(request):
    print("whatsapp_webhook called.")
    print(f"Request method: {request.method}")

    if request.method == 'GET':
        print("Received GET request for verification.")
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        print(f"verify_token from GET: {verify_token}")
        print(f"challenge from GET: {challenge}")

        if verify_token == VERIFY_TOKEN:
            print("Verify token matched. Returning challenge.")
            return HttpResponse(challenge, status=200)
        else:
            print("Verification token mismatch. Returning 403.")
            return HttpResponse("Verification token mismatch", status=403)

    elif request.method == 'POST':
        print("Handling POST request (incoming webhook).")

        try:
            # Decode incoming JSON
            incoming_data = json.loads(request.body.decode('utf-8'))
            print("Incoming JSON data:", incoming_data)

            # Check for "entry"
            if "entry" not in incoming_data:
                print("No 'entry' found in incoming_data. Possibly not a valid webhook payload.")
                return HttpResponse("No 'entry' in payload", status=200)

            # Process each entry
            for entry in incoming_data.get("entry", []):
                print("Processing entry:", entry)

                for change in entry.get("changes", []):
                    print("Processing change:", change)

                    value = change.get("value", {})
                    print("Value in change:", value)

                    messages = value.get("messages", [])
                    print(f"Found {len(messages)} messages in value.")

                    # Iterate through messages
                    for msg in messages:
                        print("Processing message:", msg)

                        sender_phone = msg.get("from")
                        user_text = msg.get("text", {}).get("body", "")
                        print(f"sender_phone: {sender_phone}, user_text: {user_text}")

                        if sender_phone and user_text:
                            # Get or create conversation
                            conversation, created = Conversation.objects.get_or_create(
                                phone_number=sender_phone
                            )
                            print(f"Conversation: {conversation}, created={created}")

                            if created:
                                try:
                                    print("Creating a new thread via OpenAI client...")
                                    thread = client.beta.threads.create()
                                    conversation.thread_id = thread.id
                                    conversation.save()
                                    print(f"Thread created with ID: {thread.id}")
                                except Exception as e:
                                    print(f"ERROR creating thread: {e}")
                                    traceback.print_exc()
                                    continue
                            else:
                                thread_id = conversation.thread_id
                                print(f"Existing conversation with thread_id: {thread_id}")

                            thread_id = conversation.thread_id

                            client.beta.threads.messages.create(
                                thread_id=thread_id,
                                role="user",
                                content=user_text
                            )

                            response = get_gpt_response(thread_id)
                            send_whatsapp_message(sender_phone,response)

            return HttpResponse("Event received", status=200)

        except Exception as e:
            # Any unhandled exception inside POST processing will come here
            print("Exception in POST webhook handling:", str(e))
            traceback.print_exc()
            return HttpResponse("Internal Server Error", status=500)

    # If method is not GET or POST, return 404
    print("Invalid request method; returning 404.")
    return HttpResponse("Invalid request", status=404)

def privacy_policy(request):
    return render(request, 'index.html')
