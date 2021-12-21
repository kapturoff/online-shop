from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.Categories.as_view()),
    path('categories/<str:category_name>', views.CategoryDetails.as_view()),
    path(
        'categories/<str:category_name>/<int:product_id>',
        views.ProductDetails.as_view()
    ),
    path(
        'categories/<str:category_name>/<int:product_id>/reviews',
        views.ReviewList.as_view()
    ),
    path(
        'categories/<str:category_name>/<int:product_id>/reviews/create',
        views.ReviewCreate.as_view()
    )
]
