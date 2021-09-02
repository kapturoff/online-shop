from django.urls import path
from users_data_storage import views

urlpatterns = [
    path('users/<int:user_id>', views.UserDetail.as_view()),
    path('users/<int:user_id>/wishlist', views.Wishlist.as_view()),
]
