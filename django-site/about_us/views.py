from django.shortcuts import render

def index(request):
    return render(request, 'about_us.html')
