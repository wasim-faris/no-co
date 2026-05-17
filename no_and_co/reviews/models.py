from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField

class Review(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="reviews")
    order = models.ForeignKey("core.Order", on_delete=models.CASCADE, related_name="reviews")
    order_item = models.ForeignKey("core.OrderItem", on_delete=models.CASCADE, related_name="reviews")
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField()
    
    image1 = CloudinaryField('image', folder='reviews/', blank=True, null=True)
    image2 = CloudinaryField('image', folder='reviews/', blank=True, null=True)
    image3 = CloudinaryField('image', folder='reviews/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product", "order")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.product_name}"
