# TODO: Make it sending reviews with the product data (#95535bf4)

from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer, ProductSerializer


class Categories(generics.ListAPIView):
    '''
    This class is responsible for /categories endpoint. Returns a list of the all categories
    '''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    renderer_classes = [JSONRenderer]


class CategoryDetails(generics.RetrieveAPIView):
    ''''
    This class is responsible for /categories/<category_name> endpoint. Returns details of an certain category including a 
    list of all its items
    '''
    queryset = Category.objects.all()
    serializer_class = ProductListSerializer
    renderer_classes = [JSONRenderer]
    lookup_url_kwarg = 'category_name'

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(
            queryset, name=self.kwargs['category_name']
        )
        return obj


class ProductDetails(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    renderer_classes = [JSONRenderer]
    lookup_url_kwarg = 'product_id'
