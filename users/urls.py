from django.urls import path
from . import views


urlpatterns = [
    path('register', views.UserRegister.as_view()),
    path('users/<int:user_id>', views.UserDetail.as_view()),
    path('users/<int:user_id>/wishlist', views.Wishlist.as_view()),
    path('users/<int:user_id>/cart', views.Cart.as_view()),
]
