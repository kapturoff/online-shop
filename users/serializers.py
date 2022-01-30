from products.serializers import ProductSerializer
from rest_framework import serializers
from django.contrib.auth.models import User


class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = ProductSerializer()
    amount = serializers.IntegerField(max_value=32767, min_value=0)


class WishlistItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = ProductSerializer()

class UserSerializer(serializers.ModelSerializer):
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'date_joined', 'last_login', 'reviews_count']

    def get_reviews_count(self, user):
        return user.commentaries.count()


class RegisterSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.CharField(required=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    def validate_email(self, value):
        """
        Check that the email is unique
        """
        email_is_used = User.objects.filter(email=value)

        if email_is_used:
            raise serializers.ValidationError('The email is already taken')

        return value

    def validate_username(self, value):
        """
        Check that the username is unique
        """
        username_is_used = User.objects.filter(username=value)

        if username_is_used:
            raise serializers.ValidationError('The username is already taken')

        return value

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user
