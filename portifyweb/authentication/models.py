from django.db import models

class CustomUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)   # Set once when user is created
    is_active = models.BooleanField(default=True)          # For future deactivation use
    last_login = models.DateTimeField(null=True, blank=True)  # Optional: Update on login

    

    def __str__(self):
        return self.name



from django.db import models
from django.contrib.auth.models import User



class GoogleUser123(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # ✅ Add this field
    google_id = models.CharField(max_length=255, unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)   # Set once when user is created
    is_active = models.BooleanField(default=True)          # For future deactivation use
    last_login = models.DateTimeField(null=True, blank=True)  # Optional: Update on login
    

    def __str__(self):
        return self.user.username
    

class GoogleUser(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # ✅ Add this field
    google_id = models.CharField(max_length=255, unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)   # Set once when user is created
    is_active = models.BooleanField(default=True)          # For future deactivation use
    last_login = models.DateTimeField(null=True, blank=True)  # Optional: Update on login
    

    def __str__(self):
     return self.name  # or self.email

# models.py

class GuestSession(models.Model):
    token = models.CharField(max_length=64, unique=True)
    last_active = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=255, default='Guest_0000')
    

