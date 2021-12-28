from rest_framework.permissions import BasePermission
from products.models import Review


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.id == view.kwargs['user_id']


class IsReviewOwner(BasePermission):
    def has_permission(self, request, view):
        all_reviews_of_user = Review.objects.filter(author__id=request.user.id)
        IDs = [review.id for review in all_reviews_of_user]

        return view.kwargs['review_id'] in IDs