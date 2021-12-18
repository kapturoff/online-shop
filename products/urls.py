from django.urls import path
from . import views

urlpatterns = [
    # path('snippets/', views.snippet_list),
    # path('snippets/<int:pk>/', views.snippet_detail),
    path('categories', views.Categories.as_view()),
    path('categories/<str:category_name>', views.CategoryDetails.as_view()),
    path(
        'categories/<str:category_name>/<int:product_id>',
        views.ProductDetails.as_view()
    ),
    path(
        'categories/<str:category_name>/<int:product_id>/reviews',
        views.Reviews.as_view()
    ),
]
