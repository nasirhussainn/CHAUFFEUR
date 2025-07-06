from django.db import models
from api.models.booking import Booking

class PromoCode(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, unique=True, related_name="promo_code_obj")
    promo_code = models.CharField(max_length=100)
