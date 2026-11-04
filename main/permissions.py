from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can create or delete projects; editors can update them."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
            or (
                request.method in ("PUT", "PATCH")
                and request.user.is_authenticated
                and request.user.groups.filter(name="Editor").exists()
            )
        )
