from rest_framework.permissions import BasePermission
from .models import Order


class IsOrderOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            order_id = view.kwargs['order_id']
            order = Order.objects.get(id=order_id)
            return bool(order.customer.id is request.user.id
                       ) or bool(request.user.is_staff)
        except Exception as e:
            return False
