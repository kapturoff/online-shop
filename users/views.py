from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework import permissions, generics
from . import serializers, models, permissions as user_permissions
from products import models as product_models, serializers as product_serializers
from django.contrib.auth.models import User


class UserDetail(generics.RetrieveAPIView):
    '''
    Class that responsible for accessing user's data. Returns serialized User model on GET request.
    '''
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    lookup_url_kwarg = 'user_id'


class UserRegister(generics.CreateAPIView):
    '''
    Class that responsible for creating new user
    '''
    queryset = User.objects.all()
    serializer_class = serializers.RegisterSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]


class Wishlist(generics.ListCreateAPIView):
    '''
    Wishlist class is responsible for working with users' wish lists.
    To work with them via GET or POST request, user must be logged in.
    You also cannot access others user wish list, so you can get or update wish list of only that user that you're logged in.

    To add new item to user's wish list, you have to send POST request with following schema in the request body:

    {
        "product_id": <int:product ID>
    }

    TODO: Create handler for delete method (#552068c1)
    '''
    queryset = models.WishlistItem.objects.all()
    serializer_class = serializers.WishlistItemSerializer
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated, user_permissions.IsOwner]
    parser_classes = [JSONParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    lookup_field = 'product_id'

    def create(self, request, user_id):
        try:
            product_id = request.data['product_id']
            product = product_models.Product.objects.get(id=product_id)
            wishlist_item = models.WishlistItem(
                owner=request.user, product=product
            )
            wishlist_item_serialized = serializers.WishlistItemSerializer(
                wishlist_item
            )

            wishlist_item.save()

            return Response(wishlist_item_serialized.data)
        except KeyError:
            raise ParseError(
                'product_id field must be in the request body', 'invalid_data'
            )
        except product_models.Product.DoesNotExist:
            raise NotFound('product_id was not found', 'not_found')


class Cart(generics.ListCreateAPIView):
    '''
    Cart class is responsible for working with users' carts.
    To work with them via GET or POST request, user must be logged in.
    You also cannot access other user cart, so you can get or update cart of only that user that you're logged in.

    To add new item to user's cart, you have to send POST request with following schema in the request body:
    
    {
        "product_id": <int:product ID>,
        "amount": <int>
    }

    TODO: Create handler for delete method
    '''

    queryset = models.CartItem.objects.all()
    serializer_class = serializers.CartItemSerializer
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated, user_permissions.IsOwner]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    parser_classes = [JSONParser]

    def list(self, request, user_id):
        self.check_object_permissions(self.request, user_id)
        queryset = self.get_queryset().filter(owner__id=user_id)
        serialized = self.serializer_class(queryset, many=True)
        return Response(serialized.data)

    def create(self, request, user_id):
        self.check_object_permissions(self.request, user_id)

        try:
            product_id = request.data['product_id']
            amount = request.data['amount']
            product = product_models.Product.objects.get(id=product_id)
            cart_item = models.CartItem(
                owner=request.user, product=product, amount=amount
            )
            cart_item_serialized = serializers.CartItemSerializer(cart_item)
            cart_item.save()

            return Response(cart_item_serialized.data)
        except KeyError:
            raise ParseError(
                '"product_id" and "amount" fields must be in request body.',
                'invalid_data'
            )
        except product_models.Product.DoesNotExist:
            raise NotFound('Product with this ID was not found.', 'not_found')


class WishlistItemDelete(generics.DestroyAPIView):
    '''
    It deletes requested cart item from database.
    Example of using: /users/2/wishlist/3 (the request must have a DELETE method)
    '''
    queryset = models.WishlistItem.objects.all()
    serializer_class = serializers.WishlistItemSerializer
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated, user_permissions.IsOwner]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    parser_classes = [JSONParser]
    lookup_url_kwarg = 'wishlist_item_id'


class CartItemDelete(generics.DestroyAPIView):
    '''
    It deletes requested cart item from database.
    Example of using: /users/2/cart/3 (the request must have a DELETE method)
    '''
    queryset = models.CartItem.objects.all()
    serializer_class = serializers.CartItemSerializer
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated, user_permissions.IsOwner]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    parser_classes = [JSONParser]
    lookup_url_kwarg = 'cart_item_id'


class ReviewList(generics.ListAPIView):
    '''
    It responses with a list of reviews made by a requested user.
    Example of using: /users/2/reviews
    '''
    queryset = product_models.Review.objects.all()
    serializer_class = product_serializers.ReviewSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get_queryset(self):
        user_id = self.kwargs['user_id']

        try:
            product_models.User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(f'User with ID { user_id } was not found.')

        return product_models.Review.objects.filter(author__id=user_id)


class ReviewDelete(generics.DestroyAPIView):
    '''
    It deletes requested review from database.
    Example of using: /users/2/reviews/3 (the request must have a DELETE method)
    '''
    queryset = product_models.Review.objects.all()
    serializer_class = product_serializers.ReviewSerializer
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    permission_classes = [
        permissions.IsAuthenticated, user_permissions.IsReviewOwner
    ]
    lookup_url_kwarg = 'review_id'
