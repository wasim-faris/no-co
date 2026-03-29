from django.db import models


class Product(models.Model):
    product_name = models.CharField(max_length=255)

    description_fit = models.TextField(blank=True, null=True)
    materials = models.TextField(blank=True, null=True)
    care_guide = models.TextField(blank=True, null=True)
    delivery_returns = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        'category.Category',
        on_delete=models.CASCADE,
        related_name="products"
    )

    subcategory = models.ForeignKey(
        'category.Subcategory',
        on_delete=models.CASCADE,
        related_name="products"
    )
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

class Variant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    sku = models.CharField(max_length=100, unique=True)

    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_sku(self):
        category = self.product.category.category_name[:2].upper()
        product = self.product.product_name[:6].upper().replace(" ", "")
        color = self.color[:3].upper()
        size = self.size.upper()

        return f"{category}-{product}-{color}-{size}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} - {self.size} - {self.color}"


class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
