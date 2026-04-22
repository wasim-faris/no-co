

from django.db import models
from products.models import Product
from category.models import Category
class Offer(models.Model):
    APPLY_CHOICES = [
        ('product', 'Product'),
        ('category', 'Category'),
    ]

    DISCOUNT_TYPE = [
        ('percentage', 'Percentage'),
        ('flat', 'Flat'),
    ]

    name = models.CharField(max_length=255)
    apply_to = models.CharField(max_length=20, choices=APPLY_CHOICES)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
# offers/models.py

class OfferProduct(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class OfferCategory(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
