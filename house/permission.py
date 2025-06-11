from rest_framework import permissions

from users.models import FaceComparison


class IsOwner(permissions.BasePermission):
    """
    Faqat uy egasiga tegishli bo‘lgan e’lonlarga kirishga ruxsat.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsFaceVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        last_check = FaceComparison.objects.filter(user=user).order_by('-created_at').first()
        return last_check is not None and last_check.match_result is True
