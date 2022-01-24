from django.db import models
from django.contrib.auth.models import User
from products.models import Product

DEFAULT_ORDER_STATUS_ID = 1  # ID of status "Created"


class OrderStatus(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    final_cost = models.FloatField()
    created = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(
        OrderStatus, default=DEFAULT_ORDER_STATUS_ID, on_delete=models.RESTRICT
    )

    # TODO: Create seperate models for addresses
    address_to_send = models.CharField(max_length=128)
    email = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    mobile_number = models.CharField(max_length=16)

    def __str__(self) -> str:
        return f'{self.customer} {self.final_cost}$'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    amount = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f'{self.product.color} {self.product.name}, {self.amount} pieces'
