from django.db import models

class Service(models.Model):
    image_cover = models.ImageField(upload_to='services/')
    image1 = models.ImageField(upload_to='services/')
    image2 = models.ImageField(upload_to='services/', null=True, blank=True)
    description = models.TextField()
    content = models.JSONField()
