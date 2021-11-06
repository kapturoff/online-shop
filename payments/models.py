from django.db import models
from orders.models import Order


class Payment(models.Model):
    '''
    Since this project is just an example of online shop API, any payment service will not be used here.
    The goal of this project is emulating of the work of the real online shop and this is why this model is placed here. 
    This model helps with imitating the working with the payment service.
    '''

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    payment_page_url = models.URLField(blank=True, null=True)
    '''
    In the next variable will be storing an URL to the locale endpoint (/payment/<payment_service_id>), which refers to 
    the fake payment service. In a real online shop here should be stored an URL to the payment page or this variable
    simply may not exist.
    '''

    payment_service_id = models.UUIDField(blank=True, null=True)
    '''
    Here an ID of the order from the payment service side is stored.
    '''

    secret_key = models.UUIDField()
    '''
    The secret key is simple approach to confirm the authenticity of the incoming request.
    It's responsible for the helping to defend against the attacks based on the fake notifications.

    As this is just an example of an online shop, the Payment API is going to send this secret key. In case
    of a real online shop API absolutely must not do this.
    '''
    def __str__(self) -> str:
        return f'{self.payment_page_url}'
