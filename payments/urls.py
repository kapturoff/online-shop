from django.urls import path
from . import views

urlpatterns = [
    path('order/<int:order_id>/pay', views.PaymentURL.as_view()),
    path(
        'payment/<str:payment_service_id>', views.FakePaymentService.as_view()
    ),
    path('webhooks', views.PaymentCheck.as_view()),
]
