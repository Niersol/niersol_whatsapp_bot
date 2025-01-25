import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .utils import get_gpt_response,send_whatsapp_message
from asgiref.sync import sync_to_async
from .models import Conversation
from django.conf import settings
from .tasks import process_incoming_message
from openai import OpenAI 
client = OpenAI(api_key=settings.OPENAI_API_KEY)

VERIFY_TOKEN = "03248673732"  # same token you set in Meta Dashboard

@csrf_exempt
async def whatsapp_webhook(request):
    if request.method == 'GET':
        # Verification logic
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if verify_token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse("Verification token mismatch", status=403)
    elif request.method == 'POST':
        # Handle incoming messages
        incoming_data = json.loads(request.body.decode('utf-8'))
        print(incoming_data)
        # Log or process the incoming message as needed
        # ...
        if "entry" in incoming_data:
            for entry in incoming_data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    for msg in value.get("messages", []):
                        sender_phone = msg.get("from")
                        user_text = msg.get("text", {}).get("body", "")
                        if sender_phone and user_text:
                            conversation,created = Conversation.objects.get_or_create(
                                phone_number=sender_phone
                            )
                            if created:
                                thread = client.beta.threads.create()
                                conversation.thread_id = thread.id
                                conversation.save()

                            thread_id = thread.id

                            if not conversation.is_active:
                                conversation.is_active = True
                                conversation.save()
                                process_incoming_message(sender_phone,thread_id)
                            else:
                                client.beta.threads.messages.create(
                                    thread_id=thread_id,
                                    role="user",
                                    content=user_text
                                )
                            
        return HttpResponse("Event received", status=200)

    return HttpResponse("Invalid request", status=404)


def privacy_policy(request):
    return render(request, 'index.html')
