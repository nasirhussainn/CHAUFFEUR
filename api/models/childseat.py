from django.db import models
from api.models.booking import Booking

class ChildSeat(models.Model):
    SEAT_TYPE_CHOICES = [
        ("rear_facing", "Rear Facing Seat"),
        ("forward_facing", "Forward Facing Seat"),
        ("booster", "Booster Seat"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='child_seats')
    type = models.CharField(max_length=50, choices=SEAT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * 40
        super().save(*args, **kwargs)
