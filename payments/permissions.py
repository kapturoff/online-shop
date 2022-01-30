from rest_framework.permissions import BasePermission
from .models import Payment


class IsPaymentOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            payment_service_id = view.kwargs['payment_service_id']
            payment = Payment.objects.get(payment_service_id=payment_service_id)
            return bool(payment.order.customer.id == request.user.id
                       ) or bool(request.user.is_staff)
        except Exception as e:
            return False
