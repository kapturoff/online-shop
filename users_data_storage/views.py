# FIXME: Bug with accessing wishlists.
#
# > Expected behaviour: 
# You get your wishlist when you authentificated and access /users/<your id>/wishlist, but when you 
# access other users' wishlists (for example, /users/<not your id>/wishlist) you do not receive anything or receive error.
#
# > Actual behaviour: 
# No matter what ID you passed in URL, you still be getting wishlist of user you are logged in. 
# It means that /users/1/wishlist, /users/2/wishlist, /users/<any id>/wishlist responses with wishlist of user 
# that you are logged in. 

from users_data_storage.permission import isOwner
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import generics
from users_data_storage import serializers, models
from products_data_storage import models as product_models
from django.contrib.auth.models import User


class UserDetail(generics.RetrieveAPIView):
    '''
    Methods for accessing user's data. Returns serialized User model.

    TODO: Rewrite it to skip user's wish list field 
    '''
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    renderer_classes = [JSONRenderer]
    lookup_url_kwarg = 'user_id'


class Wishlist(generics.ListCreateAPIView):
    queryset = models.WishlistItem.objects.all()
    serializer_class = serializers.WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated, isOwner]
    parser_classes = [JSONParser]

    def list(self, request, **args):
        queryset = self.get_queryset().filter(owner__id=request.user.id) # Send only those wish list items that user owns
        serialized = self.serializer_class(queryset, many=True)
        return Response(serialized.data)

    def create(self, request, user_id):
        try:
            product_id = request.data["product_id"]
            product = product_models.Product.objects.get(id=product_id)
            wishlist_item = models.WishlistItem.objects.create(owner=request.user, product=product)
            wishlist_item_serialized = serializers.WishlistItemSerializer(wishlist_item)
            wishlist_item.save()
            return Response(data=wishlist_item_serialized.data, status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except product_models.Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

# TODO: Create method for accessings users' carts.
# GET: */users/<user_id>/cart - sends cart items and their count
# POST: */users/<user_id>/cart - adds list of products to cart (should be authorized as owner of this cart)