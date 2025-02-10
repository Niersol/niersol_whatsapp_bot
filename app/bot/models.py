from django.db import models

class Business(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    phone_id = models.CharField(max_length=30)
    assistant_id = models.CharField(max_length=50)

class Conversation(models.Model):
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="businesses")
    phone_number = models.CharField(max_length=255)
    thread_id = models.CharField(max_length=255, blank=True, null=True)
    
    # This field will help lock the conversation while the Celery task is running
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.phone_number


