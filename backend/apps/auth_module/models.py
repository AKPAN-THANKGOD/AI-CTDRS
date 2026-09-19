import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
        ('viewer', 'Viewer'),
    ], default='analyst')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email