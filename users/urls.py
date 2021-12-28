from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('register', views.UserRegister.as_view()),
    path('token', obtain_auth_token, name='api_token_auth'),
    path('users/<int:user_id>', views.UserDetail.as_view()),
    path('users/<int:user_id>/wishlist', views.Wishlist.as_view()),
    path('users/<int:user_id>/wishlist/<int:wishlist_item_id>/delete', views.WishlistItemDelete.as_view()),
    path('users/<int:user_id>/cart', views.Cart.as_view()),
    path('users/<int:user_id>/cart/<int:cart_item_id>/delete', views.CartItemDelete.as_view()),
    path('users/<int:user_id>/reviews', views.ReviewList.as_view()),
]
