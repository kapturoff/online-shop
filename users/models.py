from django.db import models
from products.models import Product
from django.contrib.auth.models import User

class WishlistItem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.product.name}'


class CartItem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f'{self.product.name}'
