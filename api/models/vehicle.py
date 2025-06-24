from django.db import models

class Vehicle(models.Model):
    TYPE_CHOICES = [("SUV", "SUV"), ("sedan", "Sedan")]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    model = models.CharField(max_length=100)
    price_per_mile = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    luggages = models.PositiveIntegerField()
    passengers = models.PositiveIntegerField()
    status = models.BooleanField(default=True)  # available or not

class CarImage(models.Model):
    image = models.ImageField(upload_to='vehicle_images/')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')

class CarFeature(models.Model):
    feature = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='features')
