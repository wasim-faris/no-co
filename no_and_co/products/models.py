from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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

class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Variant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    sku = models.CharField(max_length=100, unique=True)

    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    color_hex = models.CharField(max_length=7, blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100000)]
    )

    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_sku(self):
        import random

        while True:
            category = self.product.category.category_name[:2].upper()
            product = self.product.product_name[:6].upper().replace(" ", "")
            color = self.color[:3].upper()
            size = self.size.name.upper()

            sku = f"{category}-{product}-{color}-{size}-{random.randint(100,999)}"

            if not Variant.objects.filter(sku=sku).exists():
                return sku

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()

        if self.is_deleted and self.is_default:
            self.is_default = False

        super().save(*args, **kwargs)

        if not self.is_deleted:
            if self.is_default:
                Variant.objects.filter(product=self.product, is_default=True).exclude(pk=self.pk).update(is_default=False)
                if not self.is_active:
                    Variant.objects.filter(pk=self.pk).update(is_active=True)
                    self.is_active = True
            else:
                if not Variant.objects.filter(product=self.product, is_default=True, is_deleted=False).exists():
                    self.is_default = True
                    self.is_active = True
                    Variant.objects.filter(pk=self.pk).update(is_default=True, is_active=True)
        else:
            if not Variant.objects.filter(product=self.product, is_default=True, is_deleted=False).exists():
                next_default = Variant.objects.filter(product=self.product, is_deleted=False).first()
                if next_default:
                    next_default.is_default = True
                    next_default.is_active = True
                    next_default.save()

    def delete(self, *args, **kwargs):
        is_def = self.is_default
        prod = self.product
        super().delete(*args, **kwargs)
        if is_def:
            if not Variant.objects.filter(product=prod, is_default=True, is_deleted=False).exists():
                next_default = Variant.objects.filter(product=prod, is_deleted=False).first()
                if next_default:
                    next_default.is_default = True
                    next_default.is_active = True
                    next_default.save()

    def __str__(self):
        return f"{self.product.product_name} - {self.size.name} - {self.color}"


class VariantImage(models.Model):
    variant = models.ForeignKey(
        'Variant',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='variant_images/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.variant} - {'Primary' if self.is_primary else 'Secondary'}"
