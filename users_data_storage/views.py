from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import generics
from . import serializers, models, permissions as user_permissions
from products_data_storage import models as product_models
from django.contrib.auth.models import User


class UserDetail(generics.RetrieveAPIView):
    '''
    Class that responsible for accessing user's data. Returns serialized User model on GET request.
    '''
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    renderer_classes = [JSONRenderer]
    lookup_url_kwarg = 'user_id'


class UserRegister(generics.CreateAPIView):
    '''
    Class that responsible for creating of new user. 
    '''
    queryset = User.objects.all()
    serializer_class = serializers.RegisterSerializer
    renderer_classes = [JSONRenderer]


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
    permission_classes = [permissions.IsAuthenticated, user_permissions.IsOwner]
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
            return Response(
                data={
                    'detail': 'product_id field must be in the request body.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except product_models.Product.DoesNotExist:
            return Response(
                data={'detail': f'Product with ID {user_id} was not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


# TODO: Create method for accessings users' carts.
# GET: */users/<user_id>/cart - sends cart items and their amount
# POST: */users/<user_id>/cart - adds list of products to cart (should be authorized as owner of this cart)
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
    permission_classes = [permissions.IsAuthenticated, user_permissions.IsOwner]
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
            return Response(
                data={
                    'detail':
                        'product_id and amount fields must be in request body.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except product_models.Product.DoesNotExist:
            return Response(
                data={'detail': 'Product with this ID was not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
