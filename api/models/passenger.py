from django.db import models
from api.models.booking import Booking

class Passenger(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
