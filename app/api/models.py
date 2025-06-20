import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class User(models.Model):  # You can replace this with a custom User model if needed
    id = models.CharField(primary_key=True, max_length=64)  # Google ID
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.email

class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    transcript = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="meetings", on_delete=models.CASCADE)
    chat_history = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title
