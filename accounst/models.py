from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username = models.EmailField(unique=True)
    password = models.CharField()