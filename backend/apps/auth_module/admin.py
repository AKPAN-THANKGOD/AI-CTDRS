from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'full_name']
    ordering = ['-date_joined']