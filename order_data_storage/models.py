from django.db import models
from users_data_storage.models import User
from products_data_storage.models import Product

# Create your models here.

class OrderStatus(models.Model):
    name = models.CharField(max_length=20)


class Order(models.Model):
    customer = models.ForeignKey(
        User, 
        null=True, 
        on_delete=models.SET_NULL,
    )
    final_cost = models.FloatField()
    datetime_created = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.RESTRICT)

    # Create seperated model for addresses
    address_to_send = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f'{self.email}, ${self.datetime_created}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    bought_amount = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f'{self.product.name} | {self.order}'


class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    paid_amount = models.FloatField()

    def __str__(self) -> str:
        return f'{self.order}, +{self.paid_amount}$'