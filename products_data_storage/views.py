# TODO: Remove handlers for PUT methods. 
# Any instance of these models can be created via admin page.

from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from products_data_storage import models, serializers


@api_view(['GET', 'PUT'])
@renderer_classes([JSONRenderer])
def categories(request):
    # If this function receives GET request, it sends list of all existing categories
    # If this function receives PUT method, it adds a new category and then sends data of this category (id and name) 
    if request.method == 'GET':
        categories = models.Category.objects.all()
        categories_serialized = serializers.CategorySerializer(categories, many=True)

        return Response(categories_serialized.data)
    elif request.method == 'PUT':
        categories = serializers.CategorySerializer(data=request.data)

        if categories.is_valid():
            categories.save()
            return Response(categories.data, status=status.HTTP_201_CREATED)

        return Response(categories.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@renderer_classes([JSONRenderer])
def category(request, category_name):
    # If this function receives GET request, it sends list of all products in category
    # If this function receives PUT request, it adds new product to chosen category and then sends data of this product
    try:
        category = models.Category.objects.get(name=category_name)

        if request.method == 'GET':
            products = category.product_set.all()
            products_serialized = serializers.ProductSerializer(products, many=True)
            return Response(data=products_serialized.data, status=status.HTTP_200_OK)
        elif request.method == 'PUT':
            raw_product = serializers.ProductSerializer(data=request.data) # This variable is only needed to validate data received from request

            if raw_product.is_valid():
                product = raw_product.create(category_id=category.id)
                product_serialized = serializers.ProductSerializer(product)
                product.save()

                return Response(data=product_serialized.data, status=status.HTTP_200_OK)

            return Response(status=status.HTTP_400_BAD_REQUEST)
    except models.Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def product(request, category_name, product_id):
    # This funciton only returns product data if it founds it in database
    try:
        product = models.Product.objects.get(category__name=category_name, id=product_id)
        product_serialized = serializers.ProductSerializer(product)
        return Response(product_serialized.data, status=status.HTTP_200_OK)
    except models.Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
