from django.db import models

class ServiceArea(models.Model):
    area_name = models.CharField(max_length=255)
    description = models.TextField()
    image1 = models.ImageField(upload_to='service_areas/')
    image2 = models.ImageField(upload_to='service_areas/')
    content = models.JSONField()
