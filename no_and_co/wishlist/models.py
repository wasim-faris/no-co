from django.db import models
from django.conf import settings
from products.models import Variant
# Create your models here.

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )
    variant = models.ForeignKey(
      Variant,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlist"
        unique_together = ("user", "variant")

    def __str__(self):
        return f"{self.user} - {self.variant}"
