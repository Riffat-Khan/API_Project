from rest_framework.permissions import BasePermission
from .enum import RoleChoice

class IsManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.profile.role == RoleChoice.MANAGER.value