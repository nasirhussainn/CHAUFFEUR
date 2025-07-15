from django.db import models
from django.conf import settings
from api.models.booking import Booking
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Allow decimal ratings from 0.0 to 5.0
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('5.0'))
        ]
    )

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Booking {self.booking.id} by {self.user.username}"
