from rest_framework import serializers
from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    def create(self, category_id):
        category = models.Category.objects.get(id=category_id)
        product = models.Product(**self.data, category=category)

        return product

    class Meta:
        model = models.Product
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = models.Category
        fields = "__all__"


class ReviewSerializer(serializers.Serializer):
    product = ProductSerializer()

    class Meta:
        model = models.Review
        fields = ['author', 'liked', 'product', 'review_text']
