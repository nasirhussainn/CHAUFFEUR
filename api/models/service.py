from django.db import models
import os
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from utils.slug import generate_unique_slug  

class Service(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    image_cover = models.ImageField(upload_to='services/')
    image1 = models.ImageField(upload_to='services/')
    image2 = models.ImageField(upload_to='services/', null=True, blank=True)
    description = models.TextField()
    content = models.JSONField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.description[:50])
        super().save(*args, **kwargs)


@receiver(post_delete, sender=Service)
def delete_service_images_on_delete(sender, instance, **kwargs):
    for field in ['image_cover', 'image1', 'image2']:
        image = getattr(instance, field)
        if image and os.path.isfile(image.path):
            os.remove(image.path)

@receiver(pre_save, sender=Service)
def delete_old_images_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # New object, no existing image to delete

    try:
        old_instance = Service.objects.get(pk=instance.pk)
    except Service.DoesNotExist:
        return

    for field in ['image_cover', 'image1', 'image2']:
        old_file = getattr(old_instance, field)
        new_file = getattr(instance, field)
        if old_file and old_file != new_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)