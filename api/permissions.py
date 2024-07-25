from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    # """
    # Custom permission to only allow managers to register tasks.
    # """

    def has_permission(self, request, view):
        user = request.user
        return user.profile.role == 'manager'
    
# class IsMember(BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         return user.