from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Administrator'),
        ('analyst', 'Security Analyst'),
    ], default='analyst')
    
    # Make username nullable since we use email for login
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email