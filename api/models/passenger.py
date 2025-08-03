from django.db import models
from api.models.booking import Booking

class Passenger(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
