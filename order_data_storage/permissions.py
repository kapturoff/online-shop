from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        # return super().has_permission(request, view)
        return bool(view.kwargs['order_id'] is request.user.id) or bool(request.user.is_staff)
