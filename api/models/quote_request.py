from django.db import models
from django.conf import settings
import uuid

def generate_reference():
    return str(uuid.uuid4().hex[:12]).upper()

class QuoteRequest(models.Model):
    reference = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        default=generate_reference
    )
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name="quote_requests")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    # Guest info
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("reviewed", "Reviewed"), ("confirmed", "Confirmed"), ("rejected", "Rejected")],
        default="pending"
    )

    def __str__(self):
        return f"Quote {self.reference} - {self.vehicle.model}"
