from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city         = models.CharField(max_length=100, blank=True)
    postal_code  = models.CharField(max_length=20,  blank=True)
    phone        = models.CharField(max_length=32,  blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"