from django.db import models
from api.models.booking import Booking

class Comment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
