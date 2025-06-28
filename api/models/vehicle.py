from django.db import models
import os
from django.dispatch import receiver

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

# Delete file when object is deleted
@receiver(models.signals.post_delete, sender=CarImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

# Delete old file when replacing with new one
@receiver(models.signals.pre_save, sender=CarImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = CarImage.objects.get(pk=instance.pk).image
    except CarImage.DoesNotExist:
        return
    new_file = instance.image
    if old_file != new_file and os.path.isfile(old_file.path):
        os.remove(old_file.path)
        
class CarFeature(models.Model):
    feature = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='features')
