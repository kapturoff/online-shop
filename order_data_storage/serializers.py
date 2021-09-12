from products_data_storage.models import Product
from users_data_storage.serializers import UserSerializer
from products_data_storage.serializers import ProductSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from . import models
from uuid import uuid4


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderStatus
        fields = '__all__'


class OrderItemSerializer(serializers.Serializer):
    product = ProductSerializer()
    amount = serializers.IntegerField(max_value=32767, min_value=0)


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    status = OrderStatusSerializer(default=1)
    items = OrderItemSerializer(many=True)

    def create(data, customer):
        '''
        It may seem like we shouldn't make another iteration on the given array for getting products from
        database again, and this has a point: here we expect to see an already prepared list of items that can
        be borrowed from cart of an user (and this kind of has a point too because CartItem and OrderItem
        models have almost identical fields).
        
        But the truth is that the request could contain IDs that're no longer existing
        (or even IDs that never been existing), so we need to check every item from list for existing.
        And we actually want to summarize the costs of the items to get the final cost of an order, so we can 
        use this iteration to kill two birds with one stone.
        '''

        raw_items = data['items']
        items = []
        final_cost = 0.0

        for item in raw_items:
            product = Product.objects.get(id=item['product']['id'])

            # Here we must check that an user cannot buy more products than is available in the database.
            if (product.amount_remaining < item['amount']):
                raise ValidationError(
                    f'The quantity of product with ID {product.id} is not enough to add this amount to the order.'
                )

            final_cost += round(product.price * item['amount'], 2)
            items.append({'product': product, 'amount': item['amount']})

        if not len(raw_items):
            raise ValidationError(
                'Field \'items\' must contain at least one product.'
            )

        order = models.Order(
            customer=customer,
            final_cost=final_cost,
            address_to_send=data['address_to_send'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            mobile_number=data['mobile_number'],
        )

        order.save()
        '''
        And now we need to iterate items one more time to add them to order.
        We could not make it before, because we did not create any order yet, but we was in
        need of first iteration because of we were summarizing final cost of whole order (and order
        cannot be created without final_cost field)
        
        TODO: Rewrite final cost field as getter in Order model to avoid it.
        '''
        for item in items:
            order_item = models.OrderItem(
                product=item['product'], amount=item['amount'], order=order
            )
            order_item.save()

        return order

    class Meta:
        model = models.Order
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    def create(order_id):
        order = models.Order.objects.get(id=order_id)
        payment_service_id = uuid4()
        secret_key = uuid4()
        url = f'/payment/{payment_service_id}'
        return models.Payment(
            order=order,
            payment_page_url=url,
            secret_key=secret_key,
            payment_service_id=payment_service_id
        )

    class Meta:
        model = models.Payment
        fields = '__all__'
