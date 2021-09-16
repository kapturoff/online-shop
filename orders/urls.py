from django.urls import path
from . import views


urlpatterns = [
    path('order', views.OrderCreator.as_view()),
    path('order/<int:order_id>', views.OrderDetail.as_view()),
    path('order/<int:order_id>/pay', views.PaymentURL.as_view()),
    path('payment/<str:payment_service_id>', views.FakePaymentService.as_view()),
    path('webhooks', views.PaymentCheck.as_view()),
]
