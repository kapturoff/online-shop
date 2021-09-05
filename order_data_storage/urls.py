from django.urls import path
from . import views


urlpatterns = [
    path('order', views.Order.as_view()),
    # path('orders/<int:order_id>', views.OrderDetail.as_view()),
    # path('payment/<int:order_id>', views.Payment.as_view()),
]
