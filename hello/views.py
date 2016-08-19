from django.shortcuts import render
from django.http import HttpResponse
from .forms import MessageForm
from .models import Message
from .models import Greeting
import urllib
import re

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, 'index.html')

def contact_us(request):
	messageForm = MessageForm(request.POST or None)
	confirmationText = ""
	if messageForm.is_valid():
		email = messageForm.cleaned_data.get("email")
		name = messageForm.cleaned_data.get("name")
		message = messageForm.cleaned_data.get("message")
		new_message = Message()
		new_message.email = email
		new_message.name = name
		new_message.message = message
		new_message.save()
		confirmationText = "Your message has been sent."
	context = {
		"messageForm":messageForm,
		"confirmationText":confirmationText,
	}
	return render(request, 'contact_us.html',context)

def db(request):
    greeting = Greeting()
    greeting.save()
    greetings = Greeting.objects.all()
    return render(request, 'db.html', {'greetings': greetings})

def about_us(request):
	return render(request,'about.html',{})
