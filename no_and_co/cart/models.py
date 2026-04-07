from django.db import models
from django.conf import settings
from products.models import Variant
class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    session_key = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'variant'],
                name='unique_user_variant'
            ),
            models.UniqueConstraint(
                fields=['session_key', 'variant'],
                name='unique_session_variant'
            )
        ]

    def __str__(self):
        if self.user:
            return f"{self.user} - {self.variant}"
        return f"Session {self.session_key} - {self.variant}"
