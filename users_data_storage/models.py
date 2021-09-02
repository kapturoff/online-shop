from django.db import models
from products_data_storage.models import Product
import datetime

# Create your models here.


class User(models.Model):
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    datetime_created = models.DateTimeField(auto_now=True)
    wishlist = models.ManyToManyField(Product)

    def __str__(self) -> str:
        return f'{self.email}, ${self.datetime_created}'


class Token(models.Model):
    expired_datetime = models.DateTimeField()
    logged_in_as = models.ForeignKey(
        User, 
        null=True, 
        on_delete=models.SET_NULL
    )

    def is_expired(self) -> bool:
        return self.expired_datetime > datetime.datetime.now()

class CartItem(models.Model):
    owner = models.ForeignKey(Token, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f'{self.product.name}'