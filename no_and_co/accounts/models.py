from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.


class User(AbstractUser):
    phone_number = models.CharField(max_length=13, null=True , blank=True)
    profile_photo = models.ImageField(upload_to="profile_pic/", default="accounts/images/default.jpg")
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
