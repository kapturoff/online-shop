from django.urls import path
from . import views

urlpatterns = [
    # path('snippets/', views.snippet_list),
    # path('snippets/<int:pk>/', views.snippet_detail),
    path('categories/', views.categories),
    path('categories/<str:category_name>/', views.category),
    path('categories/<str:category_name>/<int:product_id>', views.product),
]
