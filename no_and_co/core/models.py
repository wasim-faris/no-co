from django.db import models
import random
import string
from django.utils.timezone import now
# Create your models here.
from django.db import models
from django.conf import settings
from products.models import Variant
from users.models import Addresses
import random
import string
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError

def generate_order_number():
    date_part = now().strftime("%Y%m%d")
    random_part = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )
    return f"ORD-{date_part}-{random_part}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "coupon"

    def __str__(self):
        return self.code


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ("COD", "Cash on Delivery"),
        ("ONLINE", "Online Payment"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    address = models.ForeignKey(
        Addresses,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    coupon = models.ForeignKey(
       Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    order_number = models.CharField(
        max_length=25,
        unique=True,
        editable=False
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Professional E-commerce Fields
    tracking_id = models.CharField(max_length=100, blank=True, null=True)
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            while True:
                order_id = generate_order_number()
                if not Order.objects.filter(order_number=order_id).exists():
                    self.order_number = order_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.user}"

class OrderItem(models.Model):
    ITEM_STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        ("RETURN_REQUESTED", "Return Requested"),
        ("RETURN_APPROVED", "Return Approved"),
        ("RETURN_PICKUP_SCHEDULED", "Return Pickup Scheduled"),
        ("RETURN_PICKED_UP", "Return Picked Up"),
        ("RETURN_REJECTED", "Return Rejected"),
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name="order_items"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price at the time of purchase"
    )

    quantity = models.PositiveIntegerField()

    item_status = models.CharField(
        max_length=50,
        choices=ITEM_STATUS_CHOICES,
        default="PENDING"
    )

    def clean(self):
        super().clean()

        if self.pk:
            old_item = OrderItem.objects.get(pk=self.pk)
            old_status = old_item.item_status
            new_status = self.item_status

            if old_status == new_status:
                return

            valid_transitions = {
                "PENDING": ["CONFIRMED", "CANCELLED"],
                "CONFIRMED": ["PROCESSING", "CANCELLED"],
                "PROCESSING": ["SHIPPED"],
                "SHIPPED": ["OUT_FOR_DELIVERY"],
                "OUT_FOR_DELIVERY": ["DELIVERED"],
                "DELIVERED": [],
                "CANCELLED": [],
            }

            if old_status in valid_transitions and new_status in valid_transitions:
                allowed_next = valid_transitions[old_status]
                if new_status not in allowed_next:
                    raise ValidationError(f"Invalid order status transition from {old_status} to {new_status}.")

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

class OrderStatusHistory(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        ("RETURN_REQUESTED", "Return Requested"),
        ("RETURN_APPROVED", "Return Approved"),
        ("RETURN_PICKUP_SCHEDULED", "Return Pickup Scheduled"),
        ("RETURN_PICKED_UP", "Return Picked Up"),
        ("RETURN_REJECTED", "Return Rejected"),
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history"
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_status_history"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"

class ReturnRequest(models.Model):
    STATUS_CHOICES = (
        ('REQUESTED', 'Return Requested'),
        ('APPROVED', 'Return Approved'),
        ('PICKUP_SCHEDULED', 'Return Pickup Scheduled'),
        ('PICKED_UP', 'Return Picked Up'),
        ('REJECTED', 'Return Rejected'),
    )

    REFUND_STATUS_CHOICES = (
        ('N/A', 'Not Applicable'),
        ('PENDING', 'Pending'),
        ('INITIATED', 'Initiated'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    REFUND_METHOD_CHOICES = (
        ('ORIGINAL_SOURCE', 'Original Payment Source'),
        ('WALLET', 'Account Wallet'),
        ('BANK_TRANSFER', 'Bank Transfer'),
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
        max_length=50,
        choices=STATUS_CHOICES,
        default='REQUESTED'
    )

    refund_status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='N/A'
    )

    refund_method = models.CharField(
        max_length=20,
        choices=REFUND_METHOD_CHOICES,
        blank=True,
        null=True
    )

    admin_remarks = models.TextField(blank=True, null=True)


    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    pickup_completed_at = models.DateTimeField(blank=True, null=True)
    refund_initiated_at = models.DateTimeField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
