from rest_framework import serializers
from orders.models import Order
from orders.serializers import OrderSerializer
from .models import Payment
from uuid import uuid4


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    def create(order_id):
        order = Order.objects.get(id=order_id)
        payment_service_id = uuid4()
        secret_key = uuid4()
        url = f'/payment/{payment_service_id}'
        return Payment(
            order=order,
            payment_page_url=url,
            secret_key=secret_key,
            payment_service_id=payment_service_id
        )

    class Meta:
        model = Payment
        fields = '__all__'
