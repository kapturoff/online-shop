# TODO: Recreate these views using class based views.

# TODO: Make it sending reviews with the product data

from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from products_data_storage import models, serializers


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def categories(request):
    # If this function receives GET request, it sends list of all existing categories
    categories = models.Category.objects.all()
    categories_serialized = serializers.CategorySerializer(
        categories, many=True
    )

    return Response(categories_serialized.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def category(request, category_name):
    # If this function receives GET request, it sends list of all products in category
    try:
        category = models.Category.objects.get(name=category_name)
        products = category.product_set.all()
        products_serialized = serializers.ProductSerializer(products, many=True)
        return Response(
            data=products_serialized.data, status=status.HTTP_200_OK
        )
    except models.Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def product(request, category_name, product_id):
    # This funciton only returns product data if it founds it in database
    try:
        product = models.Product.objects.get(
            category__name=category_name, id=product_id
        )
        product_serialized = serializers.ProductSerializer(product)
        return Response(product_serialized.data, status=status.HTTP_200_OK)
    except models.Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
