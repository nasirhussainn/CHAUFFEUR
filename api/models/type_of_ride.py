from django.db import models

class TypeOfRide(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. "from airport", "to airport"
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
