from rest_framework.permissions import BasePermission
from subscription.models import (
    user_has_active_subscription,
)  # Assuming it's in subscription.models


class HasActiveSubscription(BasePermission):
    """
    Custom permission to check if user has active subscription for non-free courses.
    """

    def has_object_permission(self, request, view, obj):
        # If course is free, allow access
        if obj.is_free:
            return True

        # If not authenticated, deny
        if not request.user.is_authenticated:
            return False

        # Check if user has active subscription
        return user_has_active_subscription(request.user)
