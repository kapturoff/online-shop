from rest_framework import serializers
from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

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

    class Meta:
        model = models.Review
        fields = "__all__"
        depth = 2
