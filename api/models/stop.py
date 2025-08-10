from django.db import models
from api.models.booking import Booking

class Stop(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='stops')
    stop_location = models.CharField(max_length=255)
    order = models.IntegerField()
