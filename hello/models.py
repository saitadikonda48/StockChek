from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)

class Message(models.Model):
    email = models.CharField(max_length=120)
    name = models.CharField(max_length=120, default="Anonymous")
    message = models.TextField()
    def __unicode__(self):
        return self.email
