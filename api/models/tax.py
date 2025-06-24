from django.db import models

class TaxRate(models.Model):
    region_or_state = models.CharField(max_length=100)
    rate_percentage = models.DecimalField(max_digits=5, decimal_places=2)
