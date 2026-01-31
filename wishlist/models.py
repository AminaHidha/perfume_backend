from django.db import models
from django.conf import settings
from products.models import Products
from accounts.models import User



class Wishlist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    products = models.ManyToManyField(
        Products,
        related_name='wishlisted_by',
        blank=True
    )

    def __str__(self):
        return f"Wishlist - {self.user}"
