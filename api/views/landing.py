# views/landing.py
from django.shortcuts import render

def landing_view(request):
    return render(request, 'landing.html')  # Render an HTML template
