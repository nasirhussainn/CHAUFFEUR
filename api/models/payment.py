from django.db import models
from api.models.booking import Booking

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('amex', 'American Express'),
        ('credit_card', 'Credit Card'),
        ('discover', 'Discover'),
        ('mastercard', 'MasterCard'),
        ('visa', 'Visa'),
        ('cash', 'Cash'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)