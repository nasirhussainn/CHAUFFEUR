from django.db import models
from api.models.vehicle import Vehicle
from .type_of_ride import TypeOfRide
from api.models.tax import TaxRate
from django.conf import settings
class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("canceled", "Canceled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    type_of_ride = models.ForeignKey(TypeOfRide, on_delete=models.SET_NULL, null=True, related_name='bookings')
    pickup_address = models.TextField()
    dropoff_address = models.TextField()
    pickup_datetime = models.DateTimeField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    distance = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.BooleanField(default=False)
    number_of_hours = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
