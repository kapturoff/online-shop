from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    # TODO: Rewrite it to use by only has_permission method.
    # This can be achieved by comparing request.user field and request params.

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj
