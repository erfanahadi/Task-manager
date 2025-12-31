from rest_framework.permissions import BasePermission

class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user