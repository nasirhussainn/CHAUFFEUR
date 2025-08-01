from django.db import models
import os
from django.dispatch import receiver

from utils.slug import generate_unique_slug

def get_first_n_words(text, n=5):
    return ' '.join(text.strip().split()[:n])

class ServiceArea(models.Model):
    slug = models.SlugField(unique=True, blank=True) 
    area_name = models.CharField(max_length=255)
    description = models.TextField()
    image1 = models.ImageField(upload_to='service_areas/', null=True, blank=True)
    image2 = models.ImageField(upload_to='service_areas/', null=True, blank=True)
    content = models.JSONField()

    def save(self, *args, **kwargs):
        if not self.slug:
            short_description = get_first_n_words(self.description, 5)
            base_value = f"{self.area_name} {short_description}"
            self.slug = generate_unique_slug(self, base_value)
        super().save(*args, **kwargs)


# Delete files on object delete
@receiver(models.signals.post_delete, sender=ServiceArea)
def delete_service_area_images_on_delete(sender, instance, **kwargs):
    for field in ['image1', 'image2']:
        image = getattr(instance, field)
        if image and os.path.isfile(image.path):
            os.remove(image.path)

# Delete old files on update
@receiver(models.signals.pre_save, sender=ServiceArea)
def delete_old_service_area_images_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = ServiceArea.objects.get(pk=instance.pk)
    except ServiceArea.DoesNotExist:
        return
    for field in ['image1', 'image2']:
        old_file = getattr(old, field)
        new_file = getattr(instance, field)
        if old_file and old_file != new_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)
