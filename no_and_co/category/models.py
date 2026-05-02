from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name

class Subcategory(models.Model):
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="subcategories"
    )
    subcategory_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subcategory_name
