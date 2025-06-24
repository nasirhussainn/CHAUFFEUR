from django.db import models
from api.models.booking import Booking

class ChildSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='child_seats')
    type = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
