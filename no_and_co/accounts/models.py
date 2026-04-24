from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import string
import random

def generate_referral_code():
    return "NOACO-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

class User(AbstractUser):
    phone_number = models.CharField(max_length=13, null=True , blank=True, unique=True)
    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        default="profile_photos/default.jpg"
    )
    referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    def save(self, *args, **kwargs):
        if not self.referral_code:
            code = generate_referral_code()
            while User.objects.filter(referral_code=code).exists():
                code = generate_referral_code()
            self.referral_code = code
        super().save(*args, **kwargs)

class ReferralRecord(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referred_by_record')
    reward_amount_referrer = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    reward_amount_referred = models.DecimalField(max_digits=10, decimal_places=2, default=40.00)
    reward_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
