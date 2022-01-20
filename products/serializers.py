from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    reviews_count = serializers.IntegerField()
    likes_count = serializers.IntegerField()
    dislikes_count = serializers.IntegerField()

    class Meta:
        model = models.Product
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = models.Category
        fields = "__all__"


class ReviewAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    img = serializers.URLField(required=False)


class ReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    author = ReviewAuthorSerializer()

    def create(data, product_id: int, user: User):
        try:
            review_text = data['review_text']
            liked = data['liked']
            product = get_object_or_404(models.Product, id=product_id)

            review = models.Review(
                review_text=review_text,
                liked=liked,
                product=product,
                author=user
            )

            return review
        except KeyError as e:
            raise ValidationError(f'{e} field is not set.')

    class Meta:
        model = models.Review
        fields = "__all__"
        depth = 2
