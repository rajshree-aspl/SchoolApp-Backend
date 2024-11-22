from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from rest_framework import authentication
from django.contrib.auth.backends import BaseBackend

class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.user_type == 'admin':
            return True
        raise PermissionDenied("You do not have permission... Only admin has permission")




class StudentPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 'student':
            return True
        raise PermissionDenied("You do not have permission... Only students have permission")

class ParentPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 'parent':
            return True
        raise PermissionDenied("You do not have permission... Only parents have permission")

class TeacherPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 'teacher':
            return True
        raise PermissionDenied("You do not have permission... Only teachers have permission")

 

