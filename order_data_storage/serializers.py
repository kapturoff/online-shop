from users_data_storage.serializers import UserSerializer
from products_data_storage.serializers import ProductSerializer
from rest_framework import serializers
from order_data_storage import models


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderStatus
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    status = OrderStatusSerializer()

    class Meta:
        model = models.Order
        fields = "__all__"


class OrderItemSerializer(serializers.Serializer):
    order = OrderSerializer()
    product = ProductSerializer()
    bought_amount = serializers.IntegerField(max_value=32767, min_value=0)


class TransactionSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = models.Transaction
        fields = "__any__"
