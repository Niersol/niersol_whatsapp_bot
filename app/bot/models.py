from django.db import models

class Conversation(models.Model):
    phone_number = models.CharField(max_length=255, unique=True)
    thread_id = models.CharField(max_length=255, blank=True, null=True)
    
    # This field will help lock the conversation while the Celery task is running
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.phone_number
