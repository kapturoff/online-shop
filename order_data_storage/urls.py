from django.urls import path
from . import views


urlpatterns = [
    path('order', views.OrderCreator.as_view()),
    path('order/<int:order_id>', views.OrderDetail.as_view()),
    # path('payment/<int:order_id>', views.Payment.as_view()),
]
