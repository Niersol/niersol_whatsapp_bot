import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import get_gpt_response,send_whatsapp_message

VERIFY_TOKEN = "03248673732"  # same token you set in Meta Dashboard

@csrf_exempt
def whatsapp_webhook(request):
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
            for entry in incoming_data["entry"]:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    for msg in messages:
                        # Extract the phone number from msg['from']
                        sender_phone = msg.get("from")
                        # Extract the text from msg.get("text", {}).get("body")
                        user_text = msg.get("text", {}).get("body", "")
                        
                        # Use GPT to get a response
                        bot_reply = get_gpt_response(user_text)
                        
                        # Send the response to the user on WhatsApp
                        send_whatsapp_message(sender_phone, bot_reply)

        return HttpResponse("Event received", status=200)

    return HttpResponse("Invalid request", status=404)

from django.shortcuts import render

def privacy_policy(request):
    return render(request, 'index.html')
