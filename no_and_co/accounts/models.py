from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    phone_number = models.CharField(max_length=13, null=True , blank=True)
    profile_photo = models.ImageField(upload_to="profile_pic/", default="accounts/images/default.jpg")
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
