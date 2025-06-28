from django.db import models
from api.models.booking import Booking

class FlightInformation(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="flight_info")
    flight_number = models.CharField(max_length=50)
    airline_name = models.CharField(max_length=100)
    meet_and_greet = models.BooleanField(default=False)
    arrival_time = models.DateTimeField()

