from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class EmailVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_verified = models.BooleanField(default=False)
    expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expiry

    def __str__(self):
        return f"{self.user.email} - Verified: {self.is_verified}"
