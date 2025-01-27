from django.contrib import admin
from django.urls import path,include
from bot.views import whatsapp_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook', whatsapp_webhook, name='whatsapp_webhook'),
    path('',include('bot.urls'))
]
