from products.serializers import ProductSerializer
from . import models
from rest_framework import serializers
from django.contrib.auth.models import User


class CartItemSerializer(serializers.Serializer):
    product = ProductSerializer()
    amount = serializers.IntegerField(max_value=32767, min_value=0)


class WishlistItemSerializer(serializers.Serializer):
    product = ProductSerializer()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'date_joined', 'last_login']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.CharField(required=True)

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = [
            'id', 'username', 'date_joined', 'last_login', 'password', 'email'
        ]
