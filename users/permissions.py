from rest_framework.permissions import BasePermission
from products.models import Review

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.id == view.kwargs['user_id']

class IsReviewOwner(BasePermission):
    def has_permission(self, request, view):
        review = Review.objects.get(id = view.kwargs['user_id'])
        return request.user.id == review.author.id