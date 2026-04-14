from django.db import models
from django.conf import settings
from core.models import Order, OrderItem


class ReturnRequest(models.Model):
    STATUS_CHOICES = (
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REFUNDED', 'Refunded'),
    )

    RETURN_REASON_CHOICES = (
        ('WRONG_SIZE', 'Wrong Size Delivered'),
        ('DAMAGED_PRODUCT', 'Damaged Product'),
        ('NOT_AS_DESCRIBED', 'Not As Described'),
        ('DEFECTIVE_ITEM', 'Defective Item'),
        ('OTHER', 'Other'),
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='returns'
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='returns'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='return_requests'
    )

    reason = models.CharField(
        max_length=50,
        choices=RETURN_REASON_CHOICES
    )
    description = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REQUESTED'
    )

    is_eligible = models.BooleanField(default=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)
