from django.db import models
from django.conf import settings
# Create your models here.

class Addresses(models.Model):
    ADDRESS_TYPE = (
        ("home", "Home"),
        ("work", "Work"),
        ("other", "Other")
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name="addresses")
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=13)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255 , blank=True , null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE,
        default="home"
    )

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
