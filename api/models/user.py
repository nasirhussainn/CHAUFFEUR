from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    new_user_discount_used = models.BooleanField(
        default=False,
        help_text="True if the user has already used or forfeited the new user discount."
    )

    # You already have first_name, last_name, email, password from AbstractUser