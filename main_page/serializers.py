from rest_framework import serializers
from products.serializers import CategorySerializer
from main_page import models


class ParentCategorySerializer(serializers.ModelSerializer):
    sub_categories = CategorySerializer(many=True)

    class Meta:
        model = models.ParentCategory
        fields = '__all__'

class MainPageCarouselItemSerializer(serializers.ModelSerializer):
    class Meta:
        models = models.MainPageCarouselItem
        fields = '__all__'