from django.db import models
from django.contrib.auth.models import User
from products.models import Product

DEFAULT_ORDER_STATUS_ID = 1  # ID of status "Created"


class OrderStatus(models.Model):
    name = models.CharField(max_length=20)

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
    address_to_send = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f'{self.customer} {self.created}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    amount = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f'{self.product.color} {self.product.name}, {self.amount} pieces'


class Payment(models.Model):
    '''
    Since this project is just an example of online shop API, any payment service will not be used here.
    The goal of this project is emulating of the work of the real online shop and this is why this model is placed here. 
    This model helps with imitating the working with the payment service.
    '''

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    payment_page_url = models.URLField(blank=True, null=True)
    '''
    In the next variable will be stored an URL to locale endpoint (/payment/<payment_service_id>) which refers to 
    the fake payment service. In a real online shop here should be stored an URL to the payment page of the payment service.
    '''

    payment_service_id = models.UUIDField(blank=True, null=True)
    '''
    Here we're going to store an ID of the order on the payment service side.
    '''

    secret_key = models.UUIDField()
    '''
    The secret key is simple approach to confirm the authenticity of the incoming request.
    It's responsible for the helping to defend against the attacks based on the fake notifications.

    As this is just an example of an online shop, the Payment API is going to send this secret key. In case
    of a real online shop it absolutely must not do this.
    '''
    def __str__(self) -> str:
        return f'{self.payment_page_url}'
