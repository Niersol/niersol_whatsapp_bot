from django.contrib import admin
from django.urls import path,include
from bot.views import whatsapp_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook', whatsapp_webhook, name='whatsapp_webhook'),
<<<<<<< HEAD
=======
    path('',include('bot.urls'))
>>>>>>> 123dc62 (updated privacy policy)
]
