from orders.models import Order 
from .models import Payment
from .serializers import PaymentSerializer
from rest_framework.exceptions import APIException, ValidationError


def call_payment_service_api(order_id):
    '''
    This method just emulates the work with payment service since project does not use a real one.
    '''

    try:
        payment = Payment.objects.get(order__id=order_id)
        payment_serialized = PaymentSerializer(payment)
        return payment_serialized
    except Payment.DoesNotExist:
        '''
        In a real online shop here will be a request for the Payment service API for the creating
        of a new order. When it gets response from that API, it saves an URL for redirecting to paying page.

        It has been done to prevent a user from the recreating orders on a third-party API such as a payment service.

        Also in a real project we must send the secret key to a Payment service so they can present this secret key
        in request to identify theyself.
        '''

        order = Order.objects.get(id=order_id)
        if order.status.name != 'Created':
            raise APIException('This order is already paid.')

        payment = PaymentSerializer.create(order_id)
        payment.save()
        payment_serialized = PaymentSerializer(payment)
        return payment_serialized


def decrease_products_amount(order_items):
    for order_item in list(order_items):
        # Here we must check that an user cannot buy more products than is available in the database.
        if (order_item.product.amount_remaining < order_item.amount):
            raise ValidationError(
                f'The quantity of product with ID {order_item.product.id} is not enough to add this amount to the order.'
            )

        # Decreases amount of the products
        order_item.product.amount_remaining = order_item.product.amount_remaining - order_item.amount

        order_item.product.save()
