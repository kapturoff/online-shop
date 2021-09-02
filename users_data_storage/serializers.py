# from django.contrib.auth.models import User
# from users_data_storage import models, serializers

from rest_framework.relations import SlugRelatedField
from products_data_storage.serializers import ProductSerializer
from users_data_storage import models
from rest_framework import serializers
from django.contrib.auth.models import User


class CartItemSerializer(serializers.Serializer):
    product = ProductSerializer()
    amount = serializers.IntegerField(max_value=32767, min_value=0)


class WishlistItemSerializer(serializers.Serializer):
    product = ProductSerializer()


class UserSerializer(serializers.ModelSerializer):
    wishlist = WishlistItemSerializer(many=True)
    cart = CartItemSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'wishlist', 'cart', 'date_joined', 'last_login']
