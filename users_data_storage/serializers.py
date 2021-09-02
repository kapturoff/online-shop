from products_data_storage.serializers import ProductSerializer
from rest_framework import serializers
from users_data_storage import models

class UserSerializer(serializers.ModelSerializer):
    wishlist = ProductSerializer(read_only=True, many=True)

    class Meta:
        model = models.User
        fields = "__any__"


class TokenSerializer(serializers.ModelSerializer):
    logged_in_as = UserSerializer()

    class Meta:
        model = models.Token
        fields ="__any__"


class CartItemSerialzer(serializers.ModelSerializer):
    owner = TokenSerializer()
    product = ProductSerializer()
    amount = serializers.IntegerField(max_value=32767, min_value=0)
