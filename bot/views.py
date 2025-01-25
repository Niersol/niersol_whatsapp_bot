import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
        
        return HttpResponse("Event received", status=200)

    return HttpResponse("Invalid request", status=404)
