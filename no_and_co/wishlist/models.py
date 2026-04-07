from django.db import models
from django.conf import settings
from products.models import Variant

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlist"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "variant"],
                name="wishlist_unique_user_variant"
            ),
            models.UniqueConstraint(
                fields=["session_key", "variant"],
                name="wishlist_unique_session_variant"
            )
        ]

    def __str__(self):
        if self.user:
            return f"{self.user} - {self.variant}"
        return f"{self.session_key} - {self.variant}"
