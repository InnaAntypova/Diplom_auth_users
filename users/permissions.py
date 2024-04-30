from rest_framework.permissions import BasePermission


class IsUserStaff(BasePermission):
    """ Проверка на Модератора или Администратора """
    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return request.method in ['GET', 'DELETE']
        return False


class IsOwner(BasePermission):
    """ Проверка на владельца """
    def has_object_permission(self, request, view, obj):
        return request.user == obj
