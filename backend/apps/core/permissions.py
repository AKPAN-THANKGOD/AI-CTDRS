from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only allow admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsAnalyst(BasePermission):
    """Allow analysts and admins"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['analyst', 'admin']


class IsAdminOrReadOnly(BasePermission):
    """Allow read for everyone, write only for admins"""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.role == 'admin'