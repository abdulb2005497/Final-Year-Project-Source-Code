from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'pages/home.html')

def services(request):
    
    return render(request, 'pages/services.html')

def contact(request):
    
    return render(request, 'pages/contact.html')

def thank_you(request):
    return HttpResponse('<p class="text-green-700 font-semibold">✅ Thank you for clicking!</p>')