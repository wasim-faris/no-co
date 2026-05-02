from django.db import models
from django.conf import settings
from core.models import Order
class Coupon(models.Model):

    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=50, unique=True)

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    min_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    usage_limit_per_user = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_active = models.BooleanField(default=True)

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class CouponUsage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} used {self.coupon.code}"
