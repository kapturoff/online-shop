from django.db import models
from django.contrib.auth.models import User
from products_data_storage.models import Product


DEFAULT_ORDER_STATUS_ID = 1 # ID of status "Created"

class OrderStatus(models.Model):
    name = models.CharField(max_length=20)


class Order(models.Model):
    customer = models.ForeignKey(
        User, 
        null=True, 
        on_delete=models.SET_NULL,
    )
    final_cost = models.FloatField()
    created = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(OrderStatus, default=DEFAULT_ORDER_STATUS_ID, on_delete=models.RESTRICT)

    # TODO: Create seperated model for addresses
    address_to_send = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f'{self.customer} {self.created}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    amount = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f'{self.product.name}, {self.order}'


class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    paid_amount = models.FloatField()

    def __str__(self) -> str:
        return f'{self.order}, +{self.paid_amount}$'
