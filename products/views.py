from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductListSerializer, ProductSerializer, ReviewSerializer


class Categories(generics.ListAPIView):
    '''
    This class is responsible for /categories endpoint. Returns a list of the all categories
    '''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]


class CategoryDetails(generics.RetrieveAPIView):
    ''''
    This class is responsible for /categories/<category_name> endpoint. Returns details of an certain category including a 
    list of all its items
    '''
    queryset = Category.objects.all()
    serializer_class = ProductListSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    lookup_url_kwarg = 'category_name'

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(
            queryset, name=self.kwargs['category_name']
        )
        return obj


class ProductDetails(generics.RetrieveAPIView):
    '''
    It responses with details of a product with ID equals <product_id>.
    Example of using: /categories/top%20clothes/5
    '''
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    lookup_url_kwarg = 'product_id'


class ReviewList(generics.ListAPIView):
    '''
    It looks for product reviews with ID equals <product_id>.
    Example of using: /categories/top%20clothes/5/reviews
    '''
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    lookup_url_kwarg = 'product_id'

    def get_queryset(self):
        product_id = self.kwargs['product_id']

        try:
            Product.objects.get(id = self.kwargs['product_id'])
        except Product.DoesNotExist:
            raise NotFound(f'Product with ID { product_id } was not found')
            
        return Review.objects.filter(product__id = product_id)


class ReviewCreate(generics.CreateAPIView):
    '''
    It creates new review for a chosen product.

    The request body for this view must contain:
    {
        liked: Boolean,
        review_text: String,
    }

    You must be logged in to create the new review.
    '''
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def create(self, request, product_id, category_name):
        review = ReviewSerializer.create(request.data, product_id, request.user)
        review_serialized = ReviewSerializer(review)
        review.save()

        return Response(review_serialized.data, status=status.HTTP_201_CREATED)